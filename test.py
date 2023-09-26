import os
import shutil
import datetime as dt
import multiprocessing as mp
from typing import NamedTuple


dir = 'test_out'
if os.path.exists(dir):
    shutil.rmtree(dir)

os.mkdir(dir)

class Program(NamedTuple):
    file_name: str
    ext: str
    type_: str

types = (
    Program('out', 'json', 'json'),
    Program('out', 'png', 'plot'),
    Program('out', 'sqlite', 'sqlite'),
    # Program('out', 'csv', 'csv'),
)

def run(type_):
    minute = dt.datetime.now().minute
    command = f"python3 traffic-bot -s test -c 1 -f 24 -t {type_.type_} -o test_out/{type_.file_name}.{type_.ext} -m {minute}"
    os.system(command)

procs = []

for type_ in types:
    proc = mp.Process(target=run, args=(type_,))
    procs.append(proc)

for proc in procs:
    proc.start()

for proc in procs:
    proc.join()
