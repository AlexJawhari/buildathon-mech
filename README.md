# mech bot (Builders Mech Royale)

Survival-first Python bot for the mechfight/1 protocol. Standard library only.

- `bot.py` the bot, `world.py` terrain/solid/line-of-sight model, `arena_grid.bin.gz` the map rasterized by `tools/build_grid.py` from the kit's `world.json`.
- `mechfight.py` is the Builders bot-kit wrapper (the kit's `python/mechfight.py`, unmodified), used under the kit's terms.
- `sim/` a local approximate simulator (not the official engine) used to compare bot variants.

Open-source code used: none beyond the Builders kit wrapper above and the Python standard library. Build-time only: numpy, scipy, Pillow for `tools/build_grid.py`.

MIT licensed, see LICENSE.
