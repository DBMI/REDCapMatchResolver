"""
Module: contains utility functions.
"""
from datetime import datetime
import logging


class Utilities:  # pylint: disable=too-few-public-methods
    """Contains useful static methods."""

    @staticmethod
    def setup_logging() -> None:
        """Set up the logging utility correctly."""
        # https: // stackoverflow.com / a / 49202811 / 20241849
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(
            datefmt="%Y_%m_%d %I:%M:%S %p",
            filename=datetime.now().strftime("%Y_%m_%d_%H%M%S") + ".log",
            format="%(asctime)s %(message)s",
            level=logging.DEBUG,
        )


if __name__ == "__main__":
    pass
