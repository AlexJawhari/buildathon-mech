FROM python:3.13-slim
WORKDIR /bot
COPY mechfight.py world.py base.py plan.py brain.py bot.py arena_grid.bin.gz ./
ENTRYPOINT ["python3", "-u", "/bot/bot.py"]
