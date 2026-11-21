# Mech Royale: what other teams' public bots teach us

Research only. Nothing was run; repos were shallow-cloned to the scratchpad (`/tmp/claude-1000/-home-alex-projects/84706a66-07c4-4658-bf02-ea662678ddd7/scratchpad/competitors/`) and read with grep and targeted reads. Repo contents were treated as untrusted data.

## Caveats

- **Scores are self-reported** by the teams in their own logs (practice mean of 16 - place over 48 matches). Nothing here is verified. Re-submission noise is about ±0.1, and any behaviour change re-rolls all 48 matches, so differences under ~0.15 are noise.
- **Team mapping is mostly unknown.** Leaderboard names matched by repo name only: Monked (jmonked), Fog of War (AbhinavDasari), Bob the builder (VivekRnx), whyMiso (whyMiso), Team Overcooked (viktor-lorentz), Team Inventors (ParishruthiGanesh), BERRYBOY (pedduvedcharan), team 2.3% (charliescull), Team-Xero (arnabxero). The repo `Osca-K/builders-buildit-mech-royale` probably belongs to BobBuildIt (4.96 on the board), but its README says "Aegis" and it has no score log, so that is unverified.
- **Not a mech bot:** `varchaskukreja/TTUN` (cited as an "outside source" in jackbalseca's LEARNINGS) is a document-processing project. Its mech-royale folder is unrelated to mechfight, so the "Wolverines" link is not confirmed.
- **Not learnable:** `whyMiso/buildathon-mech-royale` is one minified `bot.mjs` (its README says it is "built from a private source tree"). `kyoto-max/Mech_Royale` has no code files.
- Only the `mechfight/1` protocol and the public kit are shared. Our practice score is deterministic per submission, so "best submission counts" and repeated resubmissions are a measurement tool, not a strength.

## Repo table

LOC = non-test logic files (approximate). Score = best self-reported practice score, where one exists.

| Repo | Likely team | Lang | LOC | Score (self) | Notes |
|---|---|---|---|---|---|
| buildathon-mech-royale (JuanQuenga) | unknown | Python | ~6.4k | **5.00** (best seen) | Most complete write-up: sim, eval log, zone field, jet-hop nav, cube grab |
| JosiahAklog/nexus-mech-royale | NEXUS | Python | ~1.8k | 4.96 (V28.1), 4.69 (V35) | Resource-first; reports rollback decisions |
| nullat0m7/mech-royale | unknown | TS | ~2.3k | 4.46 | Detailed param-by-param logs; drop distance gain |
| bsrikumar855-dot/Mech-Royale | unknown | TS | ~3.5k | 4.00 (logged) | Single-variable experiments, EXPERIMENTS.md |
| jackbalseca/mech-royale-bot | V.exe | Python | ~1.9k | **4.21** (v19) | Best written-up A/B log (LEARNINGS.md); 48-match official deltas |
| LanceHuang245/mech-royale | unknown | Python | ~1.8k | ~4.54 (cited by V.exe, unverified) | "sneak" quiet-movement flag on by default |
| Achintya-Lakshmanan/mech-royale-bot | steelhead | TS | ~1.8k | 3.71 (rank 66/137) | Loot priority lightning > laser > mortar; drone farming |
| arnabxero/xero-mech-royale | Team-Xero | Rust | ~7.8k | 3.90 (v5) | Survival-first; concealment hold spots; logged 20+ versions |
| ppetit8/mech-royale_bot | Aegis (ppetit8) | Python | ~3.3k | 3.46 (prior best) | Repair-drop vs recovery; CHANGELOG with "not officially scored" flags |
| dmclaughlin-bit/mech-bot | Doug/Diego | TS | ~3.7k | ~2.4 to 3.5 (logs) | Huge research pipeline; measured public-match data |
| Th3r0n/mech-royale-bot | "not even close" | TS | ~4.8k | unknown | planPeek cover/peek module, econ.ts upgrade order |
| robo-fight (skandra08) | loadout-hunter | Python | ~4.2k | 2.29 (session best) | Roof camping, laser counter; roof camping lost |
| p-ea1166fe (yihao-qiao) | unknown | Python | ~3.7k | unknown | model.py / tactics / tuning split; heavy modular design |
| MAGIC-Royale (Kgc3105) | unknown | TS | ~2.9k | unknown | Grid A* with jets; zone centre push late |
| mech-royale-overcooked (viktor-lorentz) | Team Overcooked | Rust | ~3.3k | 3.04 (server best) | IDEAS.md backlog; "peek-shoot laser" idea untested |
| OSU-Hackathon/Mech-Royale (lolstershwjav) | Policy League | Python | ~2.5k | unknown | Trained tactical model choosing evade/scavenge/engage; rule controller executes |
| charliescull/mech-royale-bot | team 2.3% | Python | ~4.3k | unknown | Sound map, third-party logic (FFA only), cover module |

| bob-the-builder-2026 (VivekRnx) | Bob the builder | Python | ~3.5k | 2.67 (board, name match) | Large sim and tools; kit-derived |
| fog-of-war-mech (AbhinavDasari) | Fog of War | Python | ~2.9k | 1.23 (board, name match) | Aim / chase / fight modules with tests; low score |
| monked-mech-royale (jmonked) | Monked | Python | ~1.3k | 2.44 (board, name match) | Clean NOTES.md on rules; low score |
| whyMiso/buildathon-mech-royale | whyMiso | JS | bundle | 4.13 (board, name match) | Minified; not readable |
| Osca-K/builders-buildit-mech-royale | "Aegis" (maybe BobBuildIt) | Python | ~1.2k | unknown | Predictive aim, survival-first |
| Borovail/builders-mech-royale | unknown | Python | ~1.7k | 1.56 to 2.00 (Russian README) | Economy/secondary modules, RESEARCH.md |
| Russell-Day/builders-mech-royale | unknown | Python | ~1.8k | unknown | Standard wrapper plus bot and world |
| ParishruthiGanesh/mech-royale | Team Inventors | Python | ~1.6k | unknown | Kit-derived |
| pedduvedcharan/mech-royale-bot | BERRYBOY | Python | ~1.2k | unknown | Has SUBMISSIONS.md score log (not read) |
| r-fe04b0b7 (nash-pillai) | "Arena controller" | Python | ~1.8k | unknown | Kiting, laser release after alignment |
| teetham-t/mech-royale-pocket-comet | Pocket Comet | Python | ~0.9k | unknown | Small bot |
| tick-agent (biruk-desta) | unknown | Python | ~2.8k | unknown | Mostly kit example policy; not analysed in depth |
| zlyuan9/mech-royale-bot | unknown | Python | ~2.0k | unknown | Survival-first; defensive facing |
| trompeterm/buildathon-mech-royale | unknown | TS | ~3.0k | unknown | Zone-aware nav with climb edges; mentions submission budget |
| Warrior-hound/mech-royale | unknown | Python | ~2.3k | unknown | Not analysed in depth |
| Yiyang-Jin/mech-royale | unknown | Python | ~1.5k | unknown | Not analysed in depth |
| Mech-Bot (colton-boi) | unknown | Python | ~2.3k | unknown | strategy.txt, probe.py, world.py |
| enkyuan/aquarius | Aquarius | Python | ~3.4k | unknown | Routing around campus geometry, hard-cover breaks |
| SnowySlug/buildathon-mech | Snowy Assault | Python | ~1.2k | unknown | "Resource-snowball" hypothesis; untested |
| suzhuhui-hub/oval-warden | Urban-Ers | Python | ~1.6k | unknown | Forecasts shrinking zone |
| cyanwingsbird/Mech-Royale | kestrel | JS | small | unknown | Simple nav, A*, LOS |
| Nadipalli-Sandeep/mech-royale-bot | Cyber_Ai | Python | ~1.7k | unknown | Zone-aware, dodging, upgrades |
| orbitautomation/buildathon-mech-royale | unknown | Python | ~1.4k | unknown | Kit-derived |
| hatimwen/builders-mech-royale-2026 | unknown | Python | ~0.6k | unknown | Starter with two isolated branches |
| caitlinthaeler/mech-royale | unknown | Python | ~1.8k | unknown | Kit fork with defense-notes |
| kyoto-max/Mech_Royale | unknown | ? | 0 | n/a | No code files |

## Per-repo strategy notes (condensed)

- **buildathon-mech-royale (5.00, best seen).** Modules: `brain.py` (intent: zone rotate > fight > loot/cube > heal), `combat.py` (fire-gate p_hit, lead/slew, laser state machine, lightning cone), `threats.py` (dodge bullets/shells, `mode_guess` squad vs FFA), `navigate.py` (baked walk grid, jet hops onto roofs, zone travel-time field). Ideas used: pickup memory; cube grab after kills ("cube_greed"); `killable` ×2.5 priority; rear-exposed ×1.5; zone emergency overrides everything. Its own history shows roof weapons and far loot were removed after measurement made them worse, and juke strafing was reverted.
- **jackbalseca/mech-royale-bot (V.exe, 4.21).** Engages only mechs that shoot or aim at it (+0.23). Remembers weapon pickups seen out of view and fetches one when a slot is empty (+0.19, its best gain). Stays put when idle (+0.10). Rejected: roaming for drones/crates (-0.23), backpedalling across open streets (-0.77), random strafe (-0.09), target switching (-0.31). Upgrade order had no measurable effect.
- **nullat0m7/mech-royale (4.46).** Focus fire, stick to target, prefer low HP. Supply drops: raising the drop search distance from 220 m to 300 m gained one place-point. Passive hiding and extra farming lost (its notes: about -0.45 for hiding, and six of six farming/passive changes lost).
- **Achintya/steelhead (3.71).** Stays ahead of the zone; loot priority lightning > laser > mortar; farms NPC drones; strafes at a weapon-dependent range with lead-corrected gun. Its report shows the "two hunters, 4.58 points" split: fights with two mechs in view gave the most deaths per encounter.
- **Team-Xero (3.90).** Rust, ~0.3 ms per decision. Concealment hold spots, bullet and mortar dodging, laser-first loot, blind return fire on ghost tracks, laser-charge ducking. Solo duel and faster strafing reversals lowered the score.
- **Aegis / ppetit8 (3.46 prior best).** Strategic goal selector comparing recovery, repair drops, loot, cover and zone rotation. Changelog marks each version "not officially scored", so the change record is the useful part.
- **dmclaughlin-bit/mech-bot (~2.4 to 3.5).** Heaviest research process: GAME_CONTEXT facts, measured public replays (house bots killed each other in 62 of 65 public-match deaths, so the "house bots never fight" premise is false outside practice), a keep/revert log with thresholds. Good model for our own experiment log.
- **robo-fight (2.29 session best).** Roof camping (S1), laser counter (break line of sight when an enemy charges at it), edge guard. Its roof-all tag scored lowest among its roof variants: mortar and lightning died on the ground.
- **Th3r0n (score unknown).** `cover.ts` `planPeek`: a viewshed-based peek plan (hide, step out to fire, hide). Practice module and economy module with an explicit survival upgrade list.
- **charliescull (team 2.3%, score unknown).** Sound map built from `bearing` and `dist` plus tracked mechs. Third-party module joins fights between other mechs on the side more likely to win (FFA only).
- **LanceHuang245 (~4.54, cited).** `sneak` flag: at or below 5 m/s the mech makes no sound. V.exe's table credits it with +0.2 to +0.65, but that number is cited, not verified here.
- **OSU Policy League (unknown).** Trained tactical model picks the mode (evade, scavenge, engage, hold); a rule controller turns that into movement. Its README mentions simulator batches only.
- **mech-royale-overcooked (3.04 server best).** IDEAS.md backlog: peek-shoot laser from cover (untested), endgame HP race at the final circle, weapon choice lightning vs laser measured in FFA. Its sim said squad survival is the gate.
- **Low-scoring repos (fog-of-war 1.23, monked 2.44, bob-the-builder 2.67, Borovail 1.6 to 2.0).** Useful mostly as negative examples. Monked's NOTES.md is the cleanest rules summary. Fog of War and Bob have large sims or test suites that did not translate into score.

## Cross-cutting findings

**Measured, positive**
- Weapon acquisition is worth the walk: remembering pickups and fetching when a slot is empty (+0.19, V.exe); shortening the search cost -0.27.
- Commit to fights and finish kills rather than breaking off (+0.11, V.exe).
- Survival-first zone planning with ETA-based leave times is in every top-looking repo. Zone reaches radius 0 at about 415 s (dmclaughlin notes; monked says about 6:55), so the 480 s timeout ranking by HP almost never decides a match. Being inside the final circle with HP matters.
- Supply drops: each capture gives 3 cubes, full HP and full energy. The drop ring is 8 m, and a capture is frozen while two or more mechs are in the ring (protocol §Supply drops). Distance tuning gained one place-point (nullat0m7).
- Gun lead model with telegraph factor and a fire gate on p_hit (buildathon): measured hit rates of 0.84 to 1.00 for a standing target at 40 to 190 m, and 0.20 to 0.50 for juking targets.
- Our gun vs house bots: V.exe's spectator data shows house experts hit 36% at 120 to 160 m and our bot 62 to 94% across 40 to 160 m.

**Measured, negative (do not repeat without new evidence)**
- Roaming for drones, crates and cubes: -0.23 (V.exe), and nullat0m7 saw the same pattern.
- Backpedalling at long range: -0.77 (V.exe).
- Faster strafe reversals and random reversals: -0.09 each (V.exe). Xero's faster-strafe tag scored 3.06 vs 3.75 for its base (its STATUS.md), a larger drop than V.exe saw.
- Target switching in fights: -0.31 (V.exe).
- Roof camping as the default: robo-fight's roof-all was its lowest-scoring tag. Roof weapons and far loot were removed in buildathon-mech-royale after measurement.
- Upgrade order: no measurable effect (V.exe v18). Cube farming: +50% cubes in sim, -0.23 official (V.exe).

**Contested**
- Hiding long: nullat0m7 says passive hiding costs about 0.45 (hunters regen and gather). V.exe found stay-put-when-idle gained +0.10. The reconciling reading: idle near cover is fine, but do not drift toward far points or wait out the zone.

**Protocol facts used by teams (verified against protocol.md)**
- Sound: gun 320 m, laser 380 m, laser_charge 140 m, lightning 160 m, jet 90 m, step 40 m. Walking at or below 5 m/s is silent. Charging a laser is audible at 140 m, so charge behind cover.
- Rear hits take ×1.5. Enemy weapon type is revealed by its sound.
- Supply drops land 25 s after the call, at times 70, 140 and 210 s.

**Practice vs final**
- In practice the 15 house bots share vision and hunt the player, and they do not fight each other (the teams' own premise; public matches disagree, see dmclaughlin). In the final FFA, other bots kill each other. Ideas that depend on squad behaviour (exposure, escalation, pickups) may not transfer. Third-party entry and sound-based targeting matter more in FFA.

## Top 10 ideas, ranked

Ranking weighs measured effect, how many top-looking repos use the idea, and whether it still applies in FFA. Not a quota.

1. **Weapon memory and fetch-when-empty.** Remember pickups seen out of view; go to one when a slot is empty. Used by V.exe (+0.19 measured), buildathon-mech-royale (top, pickup memory), Overcooked (pickup memory, +0.17 sim). Applies to FFA too.
2. **Exposure discipline: fight quickly, then leave the line of sight.** Engage only mechs that shoot or aim at you; no roaming for drones, crates or cubes. V.exe (+0.23 engage rule, -0.23 roaming), nullat0m7 (drone/crate farming lost). Top-looking: yes (V.exe 4.21, nullat0m7 4.46).
3. **Zone planner with ETA-based leave times.** Compare the path ETA with time to the next shrink; leave early enough; keep an emergency override. buildathon-mech-royale (zone emergency first), dmclaughlin (zone-ETA), Th3r0n (zone), Achintya (stays ahead of the zone). Top-looking: buildathon (5.00), nullat0m7 (4.46).
4. **Supply-drop capture with generous search.** Stand alone in the 8 m ring for 4 s (3 cubes, full HP and energy). nullat0m7 found +1 place-point by widening the search from 220 m to 300 m. Used by nullat0m7, Achintya (drops in loot), others. Top-looking: nullat0m7.
5. **Predictive gun lead with a reversal-rate model and a p_hit fire gate.** buildathon's model accounts for torso slew, projectile speed, shot origin and target reversals; it holds p_hit ≥ 0.22 (0.12 under 60 m). V.exe uses a similar lead with a reversal-rate estimate. Top-looking: buildathon (5.00), V.exe (4.21).
6. **Quiet movement near enemies.** Keep under 5 m/s (no step sound) and avoid boost (90 m) and laser charge (140 m) within earshot. LanceHuang245's `sneak` flag, cited at +0.2 to +0.65 by V.exe (unverified). Protocol facts confirm the sound rules. Top-looking: unknown.
7. **Laser: charge with alignment, release on kill, break line of sight when an enemy charges at you.** buildathon (laser in the state machine, release when charge kills or p_hit ≥ 0.72; 15 of 15 hits at 40 to 100 m in its harness), robo-fight (laser counter), dmclaughlin's range data (laser 49 to 89% from 30 to 230 m vs gun 25 to 37% at 150 to 230 m). Top-looking: buildathon (5.00).
8. **Focus fire and finish kills.** Pick the target you can kill with your current burst (magazine-aware), prefer low HP, and stay on it; commit rather than break off (+0.11 V.exe). buildathon `killable` ×2.5 priority, nullat0m7 focus fire, Mech-Royale (bsrikumar) kill-confirm focus. Top-looking: buildathon, nullat0m7.
9. **Face attackers and exploit rear hits.** Rear hits take ×1.5; torso faces the most dangerous enemy; keep the front arc on threats. buildathon (`rear_exposed` ×1.5, `face_yaw`), Xero (blind return fire), many others. Do not switch targets to do it (V.exe v4: -0.31). Top-looking: buildathon.
10. **Sound-based third-party entry (FFA only).** Build a sound map from bearing and distance; join fights where one side is weakened and you are unseen. charliescull has the most complete version (FFA only). Relevant to the final FFA, where bots kill each other; no practice evidence. Top-looking: unknown.

Honourable mentions (mechanic-level, not yet measured by us): peek-shoot laser from cover (Th3r0n `planPeek`, Overcooked IDEAS #3, robo-fight); jet hops onto roofs for escape only, not camping (buildathon nav, robo-fight negative for camping).

## Notes for our own work

- Our current measured best-practice data is in our logs, not here. Use the table above as ideas to test, not as proof.
- Every idea above should be tested as a single-variable change against the official practice score, since the score is deterministic per submission and noise is about ±0.1.
- Avoid copying code from these repos; the aim is to learn ideas only.
