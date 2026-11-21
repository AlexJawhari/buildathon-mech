"""Static arena model shared by the bot and the simulator: terrain, solids, line of sight, walkability."""
import gzip, math, os
from array import array

NX, NY, MINX, MINY = 1070, 724, -513.0, -334.0
HERE = os.path.dirname(os.path.abspath(__file__))


class World:
    def __init__(self, map_dir="/arena", grid_path=None):
        t = array("h")
        with open(os.path.join(map_dir, "v2", "terrain.i16"), "rb") as f:
            t.frombytes(f.read())
        self.ter = t
        raw = gzip.open(grid_path or os.path.join(HERE, "arena_grid.bin.gz")).read()
        n = NX * NY
        a = array("h"); a.frombytes(raw[: 8 * n])
        self.lo, self.hi, self.blo, self.bhi = a[:n], a[n:2 * n], a[2 * n:3 * n], a[3 * n:4 * n]
        self.nav = raw[8 * n: 9 * n]

    def ground(self, x, y):
        fx = x - MINX; fy = y - MINY
        i = int(fx); j = int(fy)
        if i < 0 or j < 0 or i >= NX - 1 or j >= NY - 1:
            i = min(max(i, 0), NX - 2); j = min(max(j, 0), NY - 2)
        u = fx - i; v = fy - j
        t = self.ter; k = j * NX + i
        return 0.01 * ((t[k] * (1 - u) + t[k + 1] * u) * (1 - v) + (t[k + NX] * (1 - u) + t[k + NX + 1] * u) * v)

    def solid(self, x, y, z):
        i = int(x - MINX); j = int(y - MINY)
        if i < 0 or j < 0 or i >= NX or j >= NY:
            return True
        k = j * NX + i
        if self.hi[k] and self.lo[k] * 0.1 <= z <= self.hi[k] * 0.1:
            return True
        return bool(self.bhi[k]) and self.blo[k] * 0.1 <= z <= self.bhi[k] * 0.1

    def blocked_nav(self, x, y):
        i = int(x - MINX); j = int(y - MINY)
        return i < 0 or j < 0 or i >= NX or j >= NY or self.nav[j * NX + i] == 1

    def los(self, a, b, step=1.5):
        """True if the segment a->b (x,y,z) is clear of buildings, bridges and terrain."""
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        d = math.sqrt(dx * dx + dy * dy + dz * dz)
        n = max(1, int(d / step))
        for s in range(1, n):
            f = s / n
            x = a[0] + dx * f; y = a[1] + dy * f; z = a[2] + dz * f
            if self.solid(x, y, z) or z < self.ground(x, y) - 0.2:
                return False
        return True
