import time
import logging
import random
from pathlib import Path


# Simple random sleep function for simulating human-like pauses
def random_sleep(min_s=1, max_s=3):
    duration = random.uniform(min_s, max_s)
    time.sleep(duration)


def setup_logging(log_file: str = "data/logs/app.log"):
    """Set up the logging configuration."""
    Path("data/logs").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logging.info("Logging initialized.")
