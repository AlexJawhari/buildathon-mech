"""Survival-first mech bot: stay in the zone, hide in cover, kite and shoot back with lead, collect lightning/laser."""
import heapq
import json
import os
import math
import random
import time

import mechfight as mf
from world import World, MINX, MINY, NX, NY

C = 2  # coarse A* cell size in metres
CNX, CNY = NX // C, NY // C
TAU = math.tau
ADJ = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
UPG = ["nanites", "plating", "armor", "gun_damage", "servos", "reactor", "gun_mag", "gun_rate", "capacitor", "gyros", "lightning_efficiency",
       "lightning_chain", "laser_damage", "sensors", "jets"]
UPG2 = ["gun_mag", "gun_damage", "plating", "armor", "gun_rate", "nanites", "lightning_efficiency", "lightning_chain", "laser_damage", "servos", "reactor", "capacitor", "gyros", "sensors", "jets"]
PICK_W = {"lightning": 3, "laser": 2}
P = {"retreat_hp": 0.5, "outnum": 2, "lo": 55, "hi": 110, "home_frac": 0.9, "scan": 0.28, "strafe": 1.0, "near_lo": -0.7, "flip_lo": 0.4, "flip_hi": 1.1, "retreat_jit": 0.0, "farm_until": 200, "farm_r": 100, "hyst": 1, "pick_r": 90, "cube_r": 45, "tol": 1.0, "stay": 200, "fire_max": 999, "upg": 1, "tscore": 1, "pmem": 1, "drop_r": 300, "engage": 0, "sticky": 0, "sneak": 0}
if os.environ.get("MECH_P"):
    P.update(json.loads(os.environ["MECH_P"]))


def wrap(a):
    return (a + math.pi) % TAU - math.pi


def dist2(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


class Bot:
    name = "mech-econ2"

    def __init__(self, hello):
        cfg = hello["config"]
        self.cfg = cfg
        self.rng = random.Random(hello.get("seed", 0))
        self.w = World(hello["map"]["dir"])
        nav = self.w.nav
        self.cblock = bytearray()
        for j in range(CNY):
            self.cblock += nav[(C * j + 1) * NX + 1:(C * j + 1) * NX + 1 + C * CNX:C]
        self.path = []
        self.path_goal = None
        self.path_t = -99
        self.search = None
        self.hist = []
        self.strafe = 1
        self.strafe_until = 0
        self.stuck_until = 0
        self.stuck_dir = (0, 0)
        self.cover = None
        self.cover_t = -99
        self.home = None
        self.home_key = None
        self.scan = 0.0
        self.last_hp = None
        self.last_dmg_t = -99
        self.laser_hold = 0
        self.dmg_bearing = None
        self.tgt_id = None
        self.healing = False
        self.pmem = {}
        self.stay_spot = None

    # ---------------------------------------------------------------- navigation
    def cfree(self, ci, cj):
        return 0 <= ci < CNX and 0 <= cj < CNY and not self.cblock[cj * CNX + ci]

    def cell(self, x, y):
        return int((x - MINX) // C), int((y - MINY) // C)

    def nearest_free(self, ci, cj):
        for r in range(0, 12):
            for di in range(-r, r + 1):
                for dj in range(-r, r + 1):
                    if max(abs(di), abs(dj)) == r and self.cfree(ci + di, cj + dj):
                        return ci + di, cj + dj
        return ci, cj

    def astar(self, start, goal):
        """Generator: yields every ~300 expansions, finally yields ('done', path of world points) or ('fail', None)."""
        s = self.nearest_free(*self.cell(start[0], start[1]))
        g = self.nearest_free(*self.cell(goal[0], goal[1]))
        gx, gy = g
        openh = [(0.0, 0.0, s)]
        gs = {s: 0.0}
        par = {}
        n = 0
        while openh:
            f, gc, cur = heapq.heappop(openh)
            if gc > gs.get(cur, 1e18):
                continue
            if cur == g:
                pts = [cur]
                while cur in par:
                    cur = par[cur]; pts.append(cur)
                pts.reverse()
                yield ("done", [(MINX + (a + 0.5) * C, MINY + (b + 0.5) * C) for a, b in pts])
                return
            n += 1
            if n % 300 == 0:
                yield None
            if n > 40000:
                break
            ci, cj = cur
            for di, dj, cost in ADJ:
                a, b = ci + di, cj + dj
                if not self.cfree(a, b):
                    continue
                if di and dj and not (self.cfree(ci + di, cj) and self.cfree(ci, cj + dj)):
                    continue
                ng = gc + cost
                nb = (a, b)
                if ng < gs.get(nb, 1e18):
                    gs[nb] = ng
                    par[nb] = cur
                    h = math.hypot(a - gx, b - gy)
                    heapq.heappush(openh, (ng + 1.5 * h, ng, nb))
        yield ("fail", None)

    def want_path(self, goal, t):
        if self.search and self.search[0] == goal:
            return
        if self.path_goal and dist2(self.path_goal, goal) < 6 and t - self.path_t < 6:
            return
        self.search = (goal, self.astar(self.pos, goal))

    def run_search(self, t, budget):
        if not self.search:
            return
        goal, gen = self.search
        t0 = time.perf_counter()
        while time.perf_counter() - t0 < budget:
            r = next(gen, ("fail", None))
            if r and r[0] == "done":
                self.path = r[1]; self.path_goal = goal; self.path_t = t; self.search = None
                return
            if r and r[0] == "fail":
                self.path = []; self.path_goal = goal; self.path_t = t; self.search = None
                return

    def line_free(self, a, b):
        d = dist2(a, b)
        n = int(d / 2) + 1
        for k in range(1, n + 1):
            f = k / n
            if self.w.blocked_nav(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f):
                return False
        return True

    def follow(self, goal, t):
        """Unit direction toward goal along the planned path (straight if it is clear)."""
        pos = self.pos
        d = dist2(pos, goal)
        if d < 3:
            return (0.0, 0.0), d
        if d < 40 and self.line_free(pos, goal):
            return ((goal[0] - pos[0]) / d, (goal[1] - pos[1]) / d), d
        self.want_path(goal, t)
        p = self.path
        if p and self.path_goal and dist2(self.path_goal, goal) < 8:
            best = 0
            bd = 1e9
            for k, q in enumerate(p):
                dd = dist2(pos, q)
                if dd < bd:
                    bd = dd; best = k
            tgt = p[min(best + 1, len(p) - 1)]
            for k in range(min(best + 10, len(p) - 1), best, -1):
                if self.line_free(pos, p[k]):
                    tgt = p[k]; break
            dd = dist2(pos, tgt)
            if dd > 0.5:
                return ((tgt[0] - pos[0]) / dd, (tgt[1] - pos[1]) / dd), d
        return ((goal[0] - pos[0]) / d, (goal[1] - pos[1]) / d), d

    def steer(self, dx, dy):
        """Rotate the wish direction until the cell 5 m ahead is walkable."""
        if abs(dx) + abs(dy) < 1e-6:
            return dx, dy
        pos = self.pos
        base = math.atan2(dy, dx)
        for off in (0, 0.45, -0.45, 0.9, -0.9, 1.4, -1.4, 2.0, -2.0):
            a = base + off
            ca, sa = math.cos(a), math.sin(a)
            if not self.w.blocked_nav(pos[0] + ca * 5, pos[1] + sa * 5) and not self.w.blocked_nav(pos[0] + ca * 2.5, pos[1] + sa * 2.5):
                return ca * math.hypot(dx, dy), sa * math.hypot(dx, dy)
        return dx, dy

    # ---------------------------------------------------------------- tactics helpers
    def exposed(self, e, p):
        """Can enemy mech e (eye) see point p (centre or head)?"""
        ex = (e["pos"][0], e["pos"][1], e["pos"][2] + 8)
        z = self.w.ground(p[0], p[1])
        return self.w.los(ex, (p[0], p[1], z + 4.5), 2.5) or self.w.los(ex, (p[0], p[1], z + 8), 2.5)

    def pick_cover(self, enemies, zc, zr):
        pos = self.pos
        best = None
        cands = [(pos[0], pos[1])]
        for r in (8, 16, 26, 38):
            for k in range(12 if r < 20 else 16):
                a = TAU * k / (12 if r < 20 else 16) + r
                cands.append((pos[0] + r * math.cos(a), pos[1] + r * math.sin(a)))
        for c in cands:
            if self.w.blocked_nav(*c):
                continue
            if math.hypot(c[0] - zc[0], c[1] - zc[1]) > zr - 18:
                continue
            exp = sum(1 for e in enemies if self.exposed(e, c))
            tr = dist2(pos, c)
            near = min((dist2(e["pos"], c) for e in enemies), default=999)
            sc = exp * 100 + tr * 0.8 - min(near, 120) * 0.25
            if best is None or sc < best[0]:
                best = (sc, c, exp)
        return best

    def solve_lead(self, me, tg, speed, gz_off=4.5):
        """Aim [yaw,pitch] to hit a moving target with a straight, instant-speed projectile."""
        mp = (me["pos"][0], me["pos"][1], me["pos"][2] + me["stats"].get("muzzle_height", 7))
        tp = tg["pos"]; tv = tg.get("vel", [0, 0, 0])
        t = 0.0
        for _ in range(4):
            px, py, pz = tp[0] + tv[0] * t, tp[1] + tv[1] * t, tp[2] + gz_off + tv[2] * t * 0.3
            d = math.sqrt((px - mp[0]) ** 2 + (py - mp[1]) ** 2 + (pz - mp[2]) ** 2)
            t = d / speed + 0.12
        yaw = math.atan2(py - mp[1], px - mp[0])
        pit = math.atan2(pz - mp[2], math.hypot(px - mp[0], py - mp[1]))
        return yaw, max(-0.7, min(1.3, pit)), d

    def incoming(self, obs):
        """Sideways dodge vector from enemy projectiles that will pass close."""
        me = self.pos
        ax = ay = 0.0
        for p in obs["projectiles"]:
            vx, vy = p["vel"][0], p["vel"][1]
            sp = math.hypot(vx, vy)
            if sp < 1:
                continue
            rx, ry = me[0] - p["pos"][0], me[1] - p["pos"][1]
            along = (rx * vx + ry * vy) / sp
            if along < 0 or along > 80:
                continue
            cross = (rx * vy - ry * vx) / sp
            if abs(cross) < 6:
                s = 1 if cross < 0 else -1  # step away to the side we are already on
                ax += s * -vy / sp; ay += s * vx / sp
        return ax, ay

    # ---------------------------------------------------------------- zone / home
    def zone_state(self, obs):
        z = obs["zone"]
        zc = z["center"]; zr = z["radius"]
        d = math.hypot(self.pos[0] - zc[0], self.pos[1] - zc[1])
        return zc, zr, zr - d

    def pick_home(self, obs):
        z = obs["zone"]
        key = (tuple(z["next_center"]), z["next_radius"])
        if key == self.home_key and self.home:
            return self.home
        nc = z["next_center"]; nr = z["next_radius"]
        self.home_key = key
        if nr < 30:
            self.home = (nc[0], nc[1])
            return self.home
        dx, dy = self.pos[0] - nc[0], self.pos[1] - nc[1]
        d = math.hypot(dx, dy) or 1
        k = min(d, nr * P["home_frac"]) / d
        h = (nc[0] + dx * k, nc[1] + dy * k)
        # nudge to a walkable spot with some building cover nearby
        self.home = self.cover_spot(h, nc, nr)
        return self.home

    def cover_spot(self, h, nc, nr):
        """Walkable spot near h that building walls enclose the most (hard to see from afar)."""
        best = None
        cands = [h] + [(h[0] + r * math.cos(a * TAU / 10), h[1] + r * math.sin(a * TAU / 10)) for r in (10, 20, 30, 40) for a in range(10)]
        for c in cands:
            if self.w.blocked_nav(*c) or math.hypot(c[0] - nc[0], c[1] - nc[1]) > nr * 0.9:
                continue
            enc = 0
            zc = self.w.ground(*c)
            for a in range(12):
                aa = a * TAU / 12
                if not self.w.los((c[0], c[1], zc + 8), (c[0] + 45 * math.cos(aa), c[1] + 45 * math.sin(aa), zc + 8), 3):
                    enc += 1
            sc = enc * 3 - dist2(c, h) * 0.1
            if best is None or sc > best[0]:
                best = (sc, c)
        return best[1] if best else h

    # ---------------------------------------------------------------- main
    def act(self, obs):
        t0 = time.perf_counter()
        me = obs["self"]
        t = obs["t"]
        self.pos = me["pos"]
        pos = self.pos
        act = {"tick": obs["tick"]}
        if obs["offer"]:
            ids = [c["id"] for c in obs["offer"]["choices"]]
            up = UPG2 if P["upg"] else UPG
            order = sorted(range(len(ids)), key=lambda i: up.index(ids[i]) if ids[i] in up else 99)
            act["pick"] = order[0]
        hp, mhp = me["hp"], me["max_hp"]
        seen_ids = set()
        for p in obs["pickups"]:
            self.pmem[p["id"]] = (p["kind"], p["pos"]); seen_ids.add(p["id"])
        for i, (k_, pp_) in list(self.pmem.items()):
            if i not in seen_ids and dist2(pp_, pos) < 30:
                del self.pmem[i]
        for e in obs["events"]:
            if e["type"] == "damaged" and e.get("by") is not None:
                self.last_dmg_t = t
                self.dmg_bearing = e["bearing"]
        zc, zr, edge = self.zone_state(obs)
        mechs = [m for m in obs["mechs"] if m["kind"] == "mech"]
        npcs = [m for m in obs["mechs"] if m["kind"] == "npc"]
        for m in mechs:
            m["d"] = dist2(m["pos"], pos)
        mechs.sort(key=lambda m: m["d"])
        close = [m for m in mechs if m["d"] < 140]
        wpn = [(w or {}).get("kind") for w in me["weapons"]]
        slot1 = wpn[1] if len(wpn) > 1 else None
        stats = me["stats"]
        gun = me["weapons"][0]
        fire = [False, False]
        aim = None
        wish = (0.0, 0.0)
        boost = False
        mode = "idle"
        hurt_recent = t - self.last_dmg_t < 3

        # target selection
        target = None
        tkind = None
        mz = pos[2] + 7
        for m in close[:6]:
            m["los"] = self.w.los((pos[0], pos[1], mz), (m["pos"][0], m["pos"][1], m["pos"][2] + 4.5), 2.5)
        if close:
            vis = [m for m in close[:6] if m["los"]] or close
            if P["tscore"]:
                for m in vis:
                    ax, ay = pos[0] - m["pos"][0], pos[1] - m["pos"][1]
                    back = abs(wrap(math.atan2(ay, ax) - m["aim"][0])) > math.pi / 2
                    m["sc"] = m.get("hp", 1400) / (1.5 if back else 1.0) + m["d"] * 3
                vis = sorted(vis, key=lambda m: m["sc"])
            if P["engage"]:
                for m in vis:
                    ax, ay = pos[0] - m["pos"][0], pos[1] - m["pos"][1]
                    m["danger"] = m["d"] < 70 or hurt_recent or abs(wrap(math.atan2(ay, ax) - m["aim"][0])) < 0.45
                vis = [m for m in vis if m["danger"]]
            if vis:
                target = vis[0]; tkind = "mech"
                for m in vis:
                    if m["id"] == self.tgt_id and (P["sticky"] or (m["d"] < vis[0]["d"] + 25 if not P["tscore"] else m["sc"] < vis[0]["sc"] + 250)):
                        target = m
                self.tgt_id = target["id"]
        elif not close and hp > 0.6 * mhp and t < P["farm_until"] and self.pick_goal(obs, wpn) is None:
            best = None
            for kind_, lst in (("npc", npcs), ("crate", obs["crates"])):
                for m in lst:
                    d_ = dist2(m["pos"], pos)
                    if d_ < P["farm_r"] and math.hypot(m["pos"][0] - zc[0], m["pos"][1] - zc[1]) < zr - 30 and (best is None or d_ < best[0]):
                        best = (d_, m, kind_)
            if best:
                target = best[1]; tkind = best[2]
        elif npcs and hp > 0.6 * mhp:
            n = min(npcs, key=lambda m: dist2(m["pos"], pos))
            if dist2(n["pos"], pos) < 70:
                target = n; tkind = "npc"
        outnum = len(close) >= P["outnum"]
        low = hp < P["retreat_hp"] * mhp or (P["hyst"] and self.healing and hp < 0.85 * mhp)
        self.healing = low or (self.healing and hp < 0.85 * mhp)

        goal = None
        if edge < 12:
            mode = "zone"
            goal = zc
            boost = edge < 0 and me["energy"] > 10
        elif target is not None and tkind == "mech" and (low or outnum or (hurt_recent and target["d"] > 150)):
            mode = "retreat"
        elif target is not None:
            mode = "fight"
        else:
            mode = "go"

        # ---- aiming/firing at target
        if target is not None:
            tg = target
            los_ok = tg.get("los", True) if tkind == "mech" else self.w.los((pos[0], pos[1], mz), (tg["pos"][0], tg["pos"][1], tg["pos"][2] + 1.5), 2.5)
            gs = gun["stats"] if gun else {"speed": 252, "range": 230}
            yaw, pit, d = self.solve_lead(me, tg, gs["speed"], 4.5 if tkind == "mech" else (1.75 if tkind == "npc" else 1.2))
            aim = [yaw, pit]
            err = abs(wrap(yaw - me["aim"][0]))
            perr = abs(pit - me["aim"][1])
            tol = P["tol"] * max(0.035, math.atan2(2.0, max(d, 10)))
            self.dd = (los_ok, round(err, 3), round(perr, 3), round(tol, 3), gun['ammo'], gun['reload'])
            if gun and los_ok and d < gs["range"] - 10 and (d < P["fire_max"] or hurt_recent or tkind != "mech") and gun["ammo"] > 0 and gun["reload"] == 0 and err < tol and perr < 0.1:
                fire[0] = True
            if tkind == "mech" and slot1 == "lightning" and d < 42 and err < 0.4 and me["energy"] > 8:
                fire[1] = True
            if tkind == "mech" and slot1 == "laser" and los_ok and d < 250:
                lw = me["weapons"][1]
                lyaw, lpit, _ = self.solve_lead(me, tg, 1e9)
                ready = lw["cooldown"] <= 0.05 and lw.get("charge", 0) >= 0
                if ready:
                    aim = [lyaw, lpit]
                    lerr = abs(wrap(lyaw - me["aim"][0]))
                    ch = lw.get("charge", 0)
                    if ch >= lw["stats"].get("charge", 0.75) - 0.02 and lerr < tol:
                        fire[1] = False  # release
                    elif lerr < 0.25 or ch > 0:
                        fire[1] = True
                    fire[0] = False if ch > 0 else fire[0]
            if gun and not fire[0] and (gun["ammo"] == 0 or (P["upg"] and not los_ok and gun["ammo"] < gun["stats"]["mag"] * 0.6 and gun["reload"] == 0)):
                act["reload"] = True
        else:
            if gun and gun["ammo"] < gun["stats"]["mag"] * 0.5 and gun["reload"] == 0:
                act["reload"] = True
            if mode == "go" or mode == "idle":
                self.scan = wrap(self.scan + P["scan"])
                if self.dmg_bearing is not None and t - self.last_dmg_t < 4:
                    aim = [self.dmg_bearing, 0.0]
                else:
                    sn = [s for s in obs["sounds"] if s["kind"] in ("gun", "step", "boost", "laser", "mortar", "lightning")]
                    aim = [wrap(sn[0]["bearing"]), 0.0] if sn and sn[0]["dist"] != "far" else [self.scan, 0.0]

        # ---- movement
        dodge = self.incoming(obs)
        if mode == "zone":
            (wx, wy), _ = self.follow(zc, t)
            wish = (wx, wy)
        elif mode == "retreat":
            if t > self.strafe_until:
                self.strafe = self.rng.choice((-1, 1))
                self.strafe_until = t + self.rng.uniform(P['flip_lo'], P['flip_hi'])
            if t - self.cover_t > 0.6 or self.cover is None:
                b = self.pick_cover(close, zc, zr)
                self.cover = b[1] if b else None
                self.cover_t = t
            if self.cover and dist2(self.cover, pos) > 3:
                (wx, wy), _ = self.follow(self.cover, t)
                wish = (wx, wy)
            else:
                # at cover: back away from nearest enemy slowly while facing it
                e = target["pos"]
                dx, dy = pos[0] - e[0], pos[1] - e[1]
                dd = math.hypot(dx, dy) or 1
                wish = (dx / dd * 0.3, dy / dd * 0.3)
            if P["retreat_jit"] and target.get("los"):
                ex, ey = target["pos"][0] - pos[0], target["pos"][1] - pos[1]
                el = math.hypot(ex, ey) or 1
                wish = (wish[0] - ey / el * self.strafe * P["retreat_jit"], wish[1] + ex / el * self.strafe * P["retreat_jit"])
            boost = low and target["d"] < 80 and me["energy"] > 40
        elif mode == "fight":
            e = target["pos"]
            dx, dy = e[0] - pos[0], e[1] - pos[1]
            dd = math.hypot(dx, dy) or 1
            ux, uy = dx / dd, dy / dd
            if t > self.strafe_until:
                self.strafe = self.rng.choice((-1, 1))
                self.strafe_until = t + self.rng.uniform(P['flip_lo'], P['flip_hi'])
            rad = 0.0
            lo_r, hi_r = (35, 55) if tkind != "mech" else (P["lo"], P["hi"])
            if slot1 == "lightning" and tkind == "mech":
                lo_r, hi_r = 20, 38
            if dd < lo_r:
                rad = P["near_lo"]
            elif dd > hi_r:
                rad = 0.6
            wish = (ux * rad - uy * self.strafe, uy * rad + ux * self.strafe)
            if edge < 40:  # bias inward near the zone edge
                ix, iy = zc[0] - pos[0], zc[1] - pos[1]
                il = math.hypot(ix, iy) or 1
                wish = (wish[0] + ix / il * 0.8, wish[1] + iy / il * 0.8)
        else:
            if P["stay"] and edge > 45 and t < P["stay"]:
                if self.stay_spot is None:
                    self.stay_spot = self.cover_spot((pos[0], pos[1]), zc, zr)
                home = self.stay_spot
            else:
                home = self.pick_home(obs)
            # opportunistic loot when nothing hostile is near
            tgt = None
            isdrop = False
            if P["drop_r"] and hp > 0.5 * mhp and not close:
                tgt = self.drop_goal(obs)
                isdrop = tgt is not None
            if tgt is None and hp > 0.6 * mhp and not close:
                tgt = self.loot_goal(obs, me, wpn)
            g = tgt or home
            (wx, wy), d = self.follow(g, t)
            if tgt is None and d < 6:
                wish = (0.0, 0.0)
            else:
                wish = (wx, wy)
            if P["sneak"] and mechs and not isdrop:
                wish = (wish[0] * 0.42, wish[1] * 0.42)
            if tgt is not None and dist2(tgt, pos) < 3.5:
                for p in obs["pickups"]:
                    if dist2(p["pos"], pos) < 3.8:
                        act["take"] = p["id"]
            # a quiet walk once close to home
        # npc drones: keep away unless we are hunting them
        for n in npcs:
            nd = dist2(n["pos"], pos)
            if nd < 50 and target is not n and mode not in ("fight",):
                wish = (wish[0] + (pos[0] - n["pos"][0]) / nd * 0.8, wish[1] + (pos[1] - n["pos"][1]) / nd * 0.8)
        wish = (wish[0] + dodge[0] * 1.5, wish[1] + dodge[1] * 1.5)

        # stuck detection
        self.hist.append((t, pos[0], pos[1]))
        while self.hist and t - self.hist[0][0] > 2.0:
            self.hist.pop(0)
        wl = math.hypot(*wish)
        if t < self.stuck_until:
            wish = self.stuck_dir
            act["jump"] = True
            boost = me["energy"] > 20
        elif wl > 0.5 and len(self.hist) > 15 and me["grounded"]:
            h0 = self.hist[0]
            if math.hypot(pos[0] - h0[1], pos[1] - h0[2]) < 2.0:
                a = self.rng.uniform(0, TAU)
                self.stuck_dir = (math.cos(a), math.sin(a))
                self.stuck_until = t + 1.0
                self.path = []; self.path_goal = None
        if wl > 1:
            wish = (wish[0] / wl, wish[1] / wl)
        if t >= self.stuck_until:
            wish = self.steer(*wish)

        if aim is None:
            aim = [math.atan2(wish[1], wish[0]) if wl > 0.1 else me["aim"][0], 0.0]
        self.dbg = (mode, None if target is None else round(dist2(target['pos'], pos)), fire[0], getattr(self, 'dd', None))
        act.update(move=[round(wish[0], 3), round(wish[1], 3)], boost=boost, aim=[aim[0], aim[1]], fire=fire)
        # background planning with whatever budget remains
        self.run_search(t, max(0.003, 0.012 - (time.perf_counter() - t0)))
        return act

    def pick_goal(self, obs, wpn):
        """Position of the best weapon pickup worth walking to, or None."""
        if (len(wpn) > 1 and wpn[1] is not None):
            return None
        pos = self.pos
        zc, zr, edge = self.zone_state(obs)
        best = None
        plist = [{"id": i, "kind": k_, "pos": pp_} for i, (k_, pp_) in self.pmem.items()] if P["pmem"] else obs["pickups"]
        for p in plist:
            if p["kind"] not in PICK_W or p["kind"] in wpn:
                continue
            d = dist2(p["pos"], pos)
            if d > P["pick_r"] or math.hypot(p["pos"][0] - zc[0], p["pos"][1] - zc[1]) > zr - 25:
                continue
            sc = PICK_W[p["kind"]] * 40 - d
            if best is None or sc > best[0]:
                best = (sc, p["pos"])
        return best[1][:2] if best else None

    def drop_goal(self, obs):
        zc, zr, edge = self.zone_state(obs)
        for d in obs["drops"]:
            if d.get("holder") not in (None, obs["self"]["id"]):
                continue
            dd = dist2(d["pos"], self.pos)
            if dd > P["drop_r"] or math.hypot(d["pos"][0] - zc[0], d["pos"][1] - zc[1]) > zr - 20:
                continue
            if dd / 11.0 + 8 >= d["lands_in"]:
                return d["pos"][:2]
        return None

    def loot_goal(self, obs, me, wpn):
        g = self.pick_goal(obs, wpn)
        if g:
            return g
        pos = self.pos
        zc, zr, edge = self.zone_state(obs)
        for c in obs["cubes"]:
            if dist2(c["pos"], pos) < P["cube_r"] and math.hypot(c["pos"][0] - zc[0], c["pos"][1] - zc[1]) < zr - 25:
                return c["pos"][:2]
        return None


if __name__ == "__main__":
    mf.run(Bot)
