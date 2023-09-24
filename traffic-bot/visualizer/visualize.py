import csv
import matplotlib.pyplot as plt
from pprint import pprint
from pathlib import Path
from jsonwrapper import AutoSaveDict
from core import _Data
from sqlitemanager import (
    Datatype,
    DB,
)
from typing import (
    Any,
)


__all__ = (
    "_Data",
    "to_json",
    "to_png",
    "to_csv",
    "to_sqlite",
    "to_stdout",
)


def to_json(data: _Data, path: Path) -> None:
    d = AutoSaveDict(path, **data)
    d.init()
    pprint(data)


def to_png(data: _Data, path: Path) -> None:
    # FIXME: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
    # https://stackoverflow.com/questions/56656777/userwarning-matplotlib-is-currently-using-agg-which-is-a-non-gui-backend-so
    x = list(data.keys())  # Times
    y = list(map(lambda i: sum(i) / len(i) if i else 0, data.values()))  # traffic

    # Calculate the maximum y value and round it up to the nearest multiple of 1000
    plt.figure(figsize=(30, 30))
    plt.bar(x, y)
    plt.show()  # type: ignore
    plt.savefig(path)


def to_csv(data: _Data, path: Path) -> None:
    # FIXME: This doesn't format properly
    formatted = ""
    final = [list(data.keys())]

    for time_data in data.values():
        final.append(time_data)  # type: ignore

    for row in final:
        formatted += ",".join(map(str, row))
        formatted += "\n"
    with open(path, mode="w") as f:
        f.write(formatted)
    print(formatted)


def to_sqlite(data: _Data, path: Path) -> None:
    colums = {f"'{i}'": Datatype.INT for i in data}
    db = DB(str(path))
    table = db.create_table("traffic", True, **colums)

    for time, value in data.items():
        row_data = {}
        for traffic in value:
            row_data[time] = traffic
            row = table.make_row(**row_data)
            row.save()
            row_data.clear()

    print(db)


def to_stdout(data: _Data, *_: Any) -> None:
    pprint(data)