#!/usr/bin/env python3

from io import BytesIO
from itertools import product
from json import loads
from multiprocessing import Pool, cpu_count, Value
from os import makedirs
from os.path import split
from time import strptime, strftime, mktime
from urllib.request import urlopen

from PIL import Image

from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import *
from tzlocal import get_localzone

from .config import level, output_file, auto_offset, hour_offset
from .utils import set_background, get_desktop_environment

counter = None
height = 550
width = 550

def get_time_offset(latest_date):
    if (auto_offset):
        local_date = datetime.now(pytz.timezone(str(get_localzone())))
        himawari_date = datetime.now(pytz.timezone('Australia/Sydney'))
        local_offset = local_date.strftime("%z")
        himawari_offset = himawari_date.strftime("%z")

        offset = int(local_offset) - int(himawari_offset);
        offset = offset / 100

        offset_tmp = datetime.fromtimestamp(mktime(latest_date))
        offset_tmp = offset_tmp + timedelta(hours=offset)
        offset_time = offset_tmp.timetuple()

    elif (hour_offset > 0):
        offset_tmp = datetime.datetime.fromtimestamp(mktime(latest_date))
        offset_tmp = offset_tmp - datetime.timedelta(hours=hour_offset)
        offset_time = offset_tmp.timetuple()

    return offset_time

def download_chunk(args):
    global counter

    x, y, latest = args
    url_format = "http://himawari8.nict.go.jp/img/D531106/{}d/{}/{}_{}_{}.png"

    with urlopen(url_format.format(level, width, strftime("%Y/%m/%d/%H%M%S", latest), x, y)) as tile_w:
        tiledata = tile_w.read()

    with counter.get_lock():
        counter.value += 1
        print("Downloading tiles: {}/{} completed".format(counter.value, level*level), end="\r", flush=True)
    return x, y, tiledata


def main():
    global counter

    print("Updating...")
    with urlopen("http://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json") as latest_json:
        latest = strptime(loads(latest_json.read().decode("utf-8"))["date"], "%Y-%m-%d %H:%M:%S")


    print("Latest version: {} GMT\n".format(strftime("%Y/%m/%d %H:%M:%S", latest)))
    if (auto_offset | hour_offset > 0):
        offset_time = get_time_offset(latest)
        print("Offset version: {} GMT\n".format(strftime("%Y/%m/%d %H:%M:%S", offset_time)))

    png = Image.new('RGB', (width*level, height*level))

    counter = Value("i", 0)
    p = Pool(cpu_count() * level)
    print("Downloading tiles: 0/{} completed".format(level*level), end="\r")
    if (auto_offset | hour_offset > 0):
        res = p.map(download_chunk, product(range(level), range(level), (offset_time,)))
    else:
        res = p.map(download_chunk, product(range(level), range(level), (latest,)))


    for (x, y, tiledata) in res:
            tile = Image.open(BytesIO(tiledata))
            png.paste(tile, (width*x, height*y, width*(x+1), height*(y+1)))

    makedirs(split(output_file)[0], exist_ok=True)
    png.save(output_file, "PNG")

    if not set_background(output_file):
        exit("\nYour desktop environment '{}' is not supported.".format(get_desktop_environment()))

    print("\nDone!")

if __name__ == "__main__":
    main()
