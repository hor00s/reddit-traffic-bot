import os
import sys
import praw
import json
import argparse
from bot import Bot
from pathlib import Path
from core import log, _Data
from logger import get_color
from typing import (
    Dict,
    Callable,
)
from visualizer import (
    to_csv,
    to_png,
    to_json,
    to_sqlite,
    to_stdout,
    to_pickle,
    to_yaml,
)
from dotenv import (
    load_dotenv,
    find_dotenv,
)


load_dotenv(find_dotenv())
BASE_DIR = Path(__file__).parent.parent

reddit = praw.Reddit(
    client_id=os.environ["client_id"],
    client_secret=os.environ["secret"],
    user_agent=os.environ["user_agent"],
    username=os.environ["username"],
    password=os.environ["password"],
)


def main() -> int:
    types: Dict[str, Callable[[_Data, Path], None]] = {
        "plot": to_png,
        "json": to_json,
        'csv': to_csv,
        "sqlite": to_sqlite,
        "stdout": to_stdout,
        "pickle": to_pickle,
        "yaml": to_yaml,
    }
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-c", "--cicles", type=int, help="The total ammount of days to harvest data"
    )
    ap.add_argument(
        "-t",
        "--type",
        required=True,
        type=str,
        choices=list(types.keys()),
        help="Choose the output",
    )
    ap.add_argument(
        "-f",
        "--format",
        default=24,
        type=int,
        choices=[12, 24],
        help="Choose the time format",
    )
    ap.add_argument("-s", "--sub", type=str, help="Choose the name of the sub")
    ap.add_argument(
        "-o", "--output", type=str, help="Choose the desired path for the outfile"
    )
    ap.add_argument("-in", "--input", type=str, help="Input file")
    ap.add_argument(
        "-m", "--minute", type=int, help="The minute the program will run", default=0
    )
    args = vars(ap.parse_args())

    cicles = args["cicles"]
    out_type = args["type"]
    time_format = args["format"]
    sub_name = args["sub"]
    file_path = args["output"]
    in_file = args["input"]
    minute = args["minute"]

    log.custom(f"{out_type.title()}", "mode", color=get_color("red_bold"))
    log.info(f"Output file = {file_path}")
    log.info(f"Total cicles = {cicles}")
    log.info(f"Time format = {time_format} hour based")

    if in_file is None:
        bot = Bot(reddit, time_format)
        bot.harvest(sub_name, cicles, minute)
        data = bot.data
    else:
        with open(in_file, mode="r") as f:
            data = json.load(f)

    types[out_type](data, file_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
