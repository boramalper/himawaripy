#!/usr/bin/env python3

from datetime import datetime, timedelta
from io import BytesIO
from itertools import product
from json import loads
from multiprocessing import Pool, cpu_count, Value
from os import makedirs
from os.path import dirname
from time import strptime, strftime, mktime
from urllib.request import urlopen

from PIL import Image
from pytz import timezone
from tzlocal import get_localzone

from .config import level, output_file, auto_offset, hour_offset
from .utils import set_background, get_desktop_environment

counter = None
height = 550
width = 550


def get_time_offset(latest_date):
    if auto_offset:
        local_date = datetime.now(timezone(str(get_localzone())))
        himawari_date = datetime.now(timezone('Australia/Sydney'))
        local_offset = local_date.strftime("%z")
        himawari_offset = himawari_date.strftime("%z")

        offset = int(local_offset) - int(himawari_offset)
        offset /= 100

        offset_tmp = datetime.fromtimestamp(mktime(latest_date))
        offset_tmp = offset_tmp + timedelta(hours=offset)
        offset_time = offset_tmp.timetuple()

    elif hour_offset > 0:
        offset_tmp = datetime.fromtimestamp(mktime(latest_date))
        offset_tmp = offset_tmp - timedelta(hours=hour_offset)
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
        print("\rDownloading tiles: {}/{} completed".format(counter.value, level * level), end="", flush=True)
    return x, y, tiledata


def main():
    global counter

    if auto_offset and hour_offset:
        exit("You can not set `auto_offset` to True and `hour_offset` to a value that is different than zero.")
    elif hour_offset < 0:
        exit("`hour_offset` must be greater than or equal to zero. I can't get future images of Earth for now.")

    print("Updating...")
    with urlopen("http://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json") as latest_json:
        latest = strptime(loads(latest_json.read().decode("utf-8"))["date"], "%Y-%m-%d %H:%M:%S")

    print("Latest version: {} GMT".format(strftime("%Y/%m/%d %H:%M:%S", latest)))
    if auto_offset or hour_offset > 0:
        requested_time = get_time_offset(latest)
        print("Offset version: {} GMT".format(strftime("%Y/%m/%d %H:%M:%S", requested_time)))
    else:
        requested_time = latest

    print()

    png = Image.new('RGB', (width * level, height * level))

    counter = Value("i", 0)
    p = Pool(cpu_count() * level)
    print("Downloading tiles: 0/{} completed".format(level * level), end="", flush=True)
    res = p.map(download_chunk, product(range(level), range(level), (requested_time,)))

    for (x, y, tiledata) in res:
        tile = Image.open(BytesIO(tiledata))
        png.paste(tile, (width * x, height * y, width * (x + 1), height * (y + 1)))

    print("\nSaving to '%s'..." % (output_file))
    makedirs(dirname(output_file), exist_ok=True)
    png.save(output_file, "PNG")

    if not set_background(output_file):
        exit("Your desktop environment '{}' is not supported.".format(get_desktop_environment()))

    print("Done!")

if __name__ == "__main__":
    main()
