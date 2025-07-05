import os
from dotenv import load_dotenv

from app.domain.printing.spec_print_strategy import load_strategies


def load_printing_strategies():
    load_dotenv()
    stragies_path = os.getenv("PRINT_STRATEGIES_PATH")
    if stragies_path:
        load_strategies(stragies_path)


def start_up():
    load_printing_strategies()


def shut_down():
    pass
