# Mech Royale notes

## Mechanics that matter for survival (from protocol.md)

- Score = 16 - place, placement only. Our opponents are 15 house bots working as a squad that hunts us.
- Zone: radius 560 -> 380 -> 240 -> 140 -> 70 -> 25 -> 0. Hold/shrink 60/50, 45/40, 35/35, 30/30, 25/25, 15/25 s. dps 20, 35, 60, 100, 160, 260 (no armor, no regen outside). The next circle is always shown from t=0 (`zone.next_center`), so we can walk to it early. Closes fully ~6:55.
- HP 1400, regen 45 HP/s after 5 s without dealing or taking damage (not outside the zone). So breaking contact for 5 s heals a full bar in ~30 s. This is the biggest survival lever.
- Rear hits do x1.5: always keep the torso aimed at the attacker (legs and torso are independent, so retreat backwards while shooting).
- Vision: 45 m all around (buildings block), 200 m inside a 120 deg wedge around the torso aim. A seen mech stays tracked with its real position for 5 s. Sound: only moving above 5 m/s makes footsteps (40 m); gun shots carry 320 m, laser 380, lightning 160, mortar 420. Standing or creeping is silent.
- Cover: buildings, bridges and terrain block sight and shots; trees block sight only (crowns soft, trunks solid), never shots.
- Gun 45 dmg, 0.24 s, 252 m/s, 12 round mag, 2.4 s reload, no drop: lead the target. Lightning (60 dmg, 45 m, auto target in a 30 deg cone, 3 energy/shot) is the best close-range defence and needs no aiming. Laser is hitscan 315 at full 0.75 s charge, telegraphed (`charging`). Mortar adds nothing for survival and makes us a cook-off target for lasers: we never pick it up.
- Mech: walk 11.7 m/s, boost 19.5 (17 energy/s), accel 58.5 m/s^2 so strafing reversals are instant; radius 2.5, height 9.
- Cubes: +4% HP/damage each, +5% size (bigger target). Upgrade offers at 1, 3, 6, 10 cubes; we pick nanites > plating > armor > gun damage.
- Supply drops (3 cubes + full heal, 4 s alone in an 8 m ring) are contested by the squad: ignored for now.

## Simulator status

- play.joinbuilders.org is a pure viewer: the game server is remote (WebSocket `/r/<room>/live`, `mechreplay/1` frames) and nothing of the simulation or house-bot logic ships in the JS bundles (checked `game-*.js`, `play-*.js`: only rendering, replay parsing and a WebSocket client). The live rooms hold human players. One sample replay (16 house bots, no squad) is served at `/replays/mechanics-v2-16.jsonl.gz`; it names the house archetypes (expert, hard, medium, brawler, sniper, thirdparty, farmer) and shows they use laser/mortar/lightning loot and get cubes.
- So the engine could not be extracted. `sim/sim.py` is our own approximation (see its header): flat-ground physics on a 1 m grid rasterized from the real map, real zone schedule, vision and sound rules, gun/lightning/laser for the bot, gun-only scripted house squad with 4 skill levels and two knowledge modes (`vision`: squad must see/hear us; `omni`: squad always knows where we are, pessimistic). The kit example bot scores about 1.0 in it (the real baseline is 1.15), which is the only calibration we have. Treat it as a smoke test and a rough A/B tool, never as the truth: house-bot skill, weapons and hunter logic are guesses.
- Usage: `python3 sim/sim.py 150 4 vision` (matches, processes, intel mode, optional bot path); `MECH_P='{"retreat_hp":0.3}'` overrides bot parameters; `sim/ab.sh`, `sim/trace.py <seed> <intel>` prints a timeline. Noise is large: the standard error of a 150 match mean is about 0.25 points.

## Experiments (hypothesis -> result -> keep/drop)

All numbers are mean score in our approximate sim (vision/omni intel). Noise (standard error) about 0.25 at n=150-200, so differences under ~0.4 are not real.

| Hypothesis | Result | Verdict |
| --- | --- | --- |
| Baseline v1 (retreat <50% HP, 2+ enemies = retreat, fight band 55-110 m, home 0.55 of next radius) | 2.05 / 1.44 | start |
| Retreat HP threshold 0.3 / 0.7 | 1.77 / 1.55, 1.95 / 1.45 | no effect, keep 0.5 |
| Retreat only when 3+ / never when outnumbered | 1.91 / 1.26, 1.81 / 1.46 | no effect, keep 2 |
| Fight band 30-70 m / 80-150 m | 1.64 / 1.35, 1.79 / 1.43 | no effect, keep 55-110 |
| Home near the centre (0.15 of next radius) | 1.19 / 1.08 | worse: the sim squad idles near the centre |
| Home near the circle edge (0.9) | 2.05 / 1.90, with loot fix 2.59 / 1.94 | keep. Unproven for the real squad. |
| Scan with the torso when idle (0.28 rad/tick) vs not | 2.05 vs 1.47 (vision) | keep (sees hunters earlier) |
| Fix: only shoot at targets with real line of sight (remembered mechs behind walls were targeted) | 2.4 -> 2.8 on 48 matches | keep |
| Loot only when no mech within 140 m instead of none tracked at all | 2.05 -> 2.59 with home 0.9 | keep |
| Faster strafe reversals (0.15-0.45 s) / slower (0.8-1.6 s) / jitter while retreating | 2.16, 2.29, 2.17 (vision) vs 2.59 | drop, keep 0.4-1.1 s |

Kit example bot in the same sim: 1.02 (real baseline 1.15). Final v2 bot: about 2.6-2.9 vision, 1.9-2.0 omni in the sim. The real leaderboard best is 5.17, so expect the real score to differ; the sim squad is gun-only and probably weaker or different from the real one.

## Known gaps and next ideas

- Not modelled in the bot: supply drops (3 cubes + full heal), crates, NPC drones for cubes (code path exists but untested in the sim), rooftops and jetting (hunters on the ground cannot easily shoot a mech on a high roof: an unexplored hiding spot), mortar.
- Use the 4 real submissions per hour as the real A/B test: submit v2, read how the score moves, then change one thing (home placement, fight band) per submission.
- Compare weapons: with a lightning or laser in slot 1 the bot switches its fight band (lightning 20-38 m). Never measured against the real squad.
- Real unknowns: how the squad finds us (vision only, or told our position), what loot they carry, whether late in the match a corner-of-the-circle home gets squeezed by the zone.

## Round 2 (after the first real score: v2 = 2.40 on 48 matches)

- Found a real bug: v2 crashed (KeyError) whenever an NPC drone became the target, so the mech just coasted on its last action. v2.1 (023fe24) fixes it. In the sim the fix alone moved the mean from about 3.3 to about 4.2.
- protocol.md says nothing about a squad, hunters or escalation; that came from the track brief, so whether escalation depends on kills or on time is unknown. A/B it on the real scorer.
- Sim recalibrated: squad members all shoot on sight, hunters (weakest skill first) path toward us, 1 + dead/2 hunters until 300 s then all; NPC drones, crates, cubes and upgrade offers added. Baseline now 3.3-4.2 vs the real 2.40, so the sim is still optimistic. Our hit rate is 0.83 vs 0.45 for the house bots; both sides trade evenly in early duels mostly because several squad members see us at once.
- Passive squad (only hunters shoot) scores 6.4 in the sim, far above the real 2.40, so real squad members do engage on sight.
- Variants (all differ only by the `P` defaults in bot.py):
  - 023fe24 v2.1: crash fix only. Sim 4.27 / 4.07 (vision / omni).
  - db23d0f mech-econ: farm crates and NPC drones until 200 s, hide at a cover spot near spawn until the zone edge is 45 m away, heal to 85% HP before re-engaging. Sim about 4.5 / 4.3.
  - fdeb3bf mech-stealth: hide until the zone forces a move (up to 400 s), do not fire at mechs beyond 80 m unless hit, heal to 85%. Sim 3.75 / 3.65 (the sim squad does not depend on our kills, so it cannot show the benefit of a kill throttle).
- Sim A/B at n=150 (SE about 0.25): farm +0.1, stay +0.1, hysteresis +0.1, pick radius 150 +0.0: all within noise.

## Round 3: diagnosis from the one real data source we have

- Real scores so far: v2 2.40, v2.1 crash fix 2.94, econ 2.98, stealth 2.38, econ2 3.06, focus 3.10.
- Practice replays are NOT fetchable: the track page lists only receipt ids, score and commit; no replay link, endpoint or game-server path exists in the page HTML, `play.joinbuilders.org` JS, or `/replays/` (404). `play.joinbuilders.org/replays/mechanics-v2-16.jsonl.gz` is the only public replay (no squad).
- The only real observation data is `kit/check/stream.jsonl.gz` (300 real observations, 37 s, one match, a bot that mostly stood still). What it shows:
  - A single house mech with gun + laser, standing off at 95-150 m, took the bot from 1400 HP to 10 in 37 s. 1260 of the ~1500 damage came from 4 laser beams of 315. The 5th beam was an early 0.2 s release that missed by 22 m.
  - The beams hit with 0.0-1.1 m error even when our bot moved at 6.7-8.1 m/s, so house lasers lead our velocity; walking in a straight line does not dodge them. A charge lasts 0.7-0.8 s and is flagged `charging: true`.
  - The house mech had its laser before t=5 s. The squad finds weapons fast.
- Sim changes: squad hard/expert members now carry a laser with a 0.75 s charge and partial lead (sim 4.65 -> 2.6, close to the real 3.0). Sim laser damage is about half of all damage we take.
- Upper bound test in the sim: starting with a laser scores 3.95 vs 2.65 without (+1.3); starting with lightning scores 2.32 (worse: it pulls us to 20-38 m while the squad stands off at 100+ m). So the second weapon must be a laser and acquiring it is the biggest lever; we only hold any second weapon in about 30-40% of sim matches and a laser in far fewer.
- Tried and dropped: beam dodging by sidestepping during the charge (laser damage 940 -> 896, no score change), scan-only or lightning-first.
- Shipped as variants J (a865161, econ base) and K (4cbe53d, focus base): laser-first loot, lightning swapped for laser, 360 degree scan at spawn, 200 m pickup radius for the first 60 s, normal fight band when holding lightning.

## Round 4: real-score variants on top of M (e46eb8d, 4.04)

- Real: M 4.04 (laser-first econ + early weapon exploration + loot after kills) is the best so far. N 83239a7 (cube greed, gun fires while laser charges) and P 5b1ea9f (run for known weapon under fire, explore to 120 s) were scored by the owner; Q e246169 = P + unvisited-cell exploration to 150 s.
- R 8301b89 (economy, `eco`/`circ`): one utility function (`econ_choice`) values cubes, laser/lightning pickups, crates and supply drops minus distance, zone exposure and nearby-enemy risk; collects during fight/retreat when the item is within 24 m (drops within 70 m); circle takes priority over detours when radius <= 150 (`circle_forced`, walks to the next circle early).
- S aa86cfb = R + duel band 40-80 m, tol 2.0 (looser fire gate). Sim only.
- T (`mech-eco-dodge`) = R + `lzdodge: 2`: when a house laser carrier with line of sight has been `charging` for `dtime` 0.4 s of its ~0.75 s charge, reverse our lateral velocity (relative to the shooter) for 0.4 s, boosting. Reason: house lasers lead our velocity, so a late reversal at release should make the beam miss; the old `lzdodge: 1` (step out of the beam line at charge start) did nothing in the sim because the shooter re-aims. Sim smoke n=40: 5.42 with vs 4.53 without (noise SE ~0.4, not evidence). Real score decides.
