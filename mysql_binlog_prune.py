#! /bin/env python3

import argparse
import os
import re
import subprocess
import sys
from collections import namedtuple
from functools import partial
from pathlib import Path

HUGE_NUMBER = 99999999999999999999999999
printe = partial(print, file=sys.stderr)

BinlogData = namedtuple('BinlogData', ['num', 'size_sum', 'size', 'path'])

# source: https://stackoverflow.com/a/72191990/551625
def parse_size(size):
    units = {"B": 1, "KB": 2**10, "MB": 2**20, "GB": 2**30, "TB": 2**40 ,
             "":  1, "KIB": 10**3, "MIB": 10**6, "GIB": 10**9, "TIB": 10**12}
    units.update({k.replace("B", ""): v for k, v in units.items() })
    m = re.match(r'''^([0-9.]+)\s*([kmgtb]{0,3})$''', str(size).strip(), re.IGNORECASE)
    number, unit = float(m.group(1)), m.group(2).upper()
    return int(number * units[unit])


parser = argparse.ArgumentParser(description="Orders mysql to delete binlogs")

parser.add_argument("--defaults-file", type=Path, default="/etc/mysql/debian.cnf", help="Path to .cnf file with login credentials for management. The default should work for all debian-based OS")
parser.add_argument("-p", "--path", required=True, type=Path, help="Path to binlog.index")
#parser.add_argument("-e", "--emergency-delete", action="store_true", help="Deletes the oldest of binlog.index.")
parser.add_argument("-n", "--number-retain", default=HUGE_NUMBER, type=int, help="Maximum number of binlog file to retain (deletes oldest first)")
parser.add_argument("-s", "--size-retain", default=HUGE_NUMBER, type=parse_size, help="Size to prune binlogs to (result will be equal or smaller than this value). Accepts same units as mysql (E.g. 1G, 25T, 2M, etc...)")
parser.add_argument("--yes", action="store_true", help="Don't prompt for confirmation. Just execute (use for automation)")

program_args = parser.parse_args()

binlog_index = Path(program_args.path)
binlog_lines = binlog_index.read_text().splitlines(keepends=False)

if not Path(program_args.defaults_file).exists():
    printe("Defaults file provided (or default value) doesn't exist. File provided:", program_args.defaults_file)
    printe("Use --defaults-file argument to provide one")
    exit(2)

os.chdir(binlog_index.parent)


def order_remove_binlog(binlog):
    operation = f"PURGE BINARY LOGS TO '{binlog.name}';"
    printe("Executting mysql query:\n", operation)
    answer = "yes" if program_args.yes else input("Confirm (y/yes)?")
    if answer.lower() in ["y", "yes"]:
        subprocess.run(
            ['mysql', '--defaults-file=' + os.fspath(program_args.defaults_file)],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            input=operation.encode("utf-8")
        )
    else:
        printe(answer, "is not 'yes'. Not executting.")

accu_size_sum = 0
binlogs = []
for i, binlog in enumerate(map(Path, binlog_lines)):
    num = len(binlog_lines) - i
    bl_size = binlog.stat().st_size
    accu_size_sum += bl_size
    binlogs.append(BinlogData(num, accu_size_sum, bl_size, binlog))


for binlog in binlogs:
    if binlog.num > program_args.number_retain:
        printe("Deleting binlog", binlog.path, "due to max of ", binlog.num, "binlogs")
        order_remove_binlog(binlog.path)
        exit(0)

    if binlog.size_sum > program_args.size_retain:
        printe("Deleting binlog", binlog.path, "due to max total size of", binlog.size_sum, "which binlogs can consume")
        order_remove_binlog(binlog.path)
        exit(0)




print(binlogs)





