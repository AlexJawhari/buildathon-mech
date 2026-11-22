"""Entry point: the planner-based decision core (brain.py) on top of the navigation and tracking code in base.py."""
import mechfight as mf
from brain import Bot

if __name__ == "__main__":
    mf.run(Bot)
