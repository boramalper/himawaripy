#!/usr/bin/env python3

""" Set near-realtime picture of Earth as your desktop background. """

__version__ = "1.2.0"

import argparse
from datetime import datetime, timedelta
from io import BytesIO
from itertools import product
from json import loads
import math
from multiprocessing import Pool, cpu_count, Value
import os
from time import strptime, strftime, mktime
from urllib.request import urlopen

import appdirs
from PIL import Image
from pytz import timezone
from tzlocal import get_localzone

from .utils import set_background, get_desktop_environment


TILE_SIZE = 550
counter = None


def get_time_offset(latest_date, hour_offset):
    if hour_offset is None:
        local_date = datetime.now(timezone(str(get_localzone())))
        himawari_date = datetime.now(timezone('Australia/Sydney'))
        local_offset = local_date.strftime("%z")
        himawari_offset = himawari_date.strftime("%z")

        offset = int(local_offset) - int(himawari_offset)
        offset /= 100

        offset_tmp = datetime.fromtimestamp(mktime(latest_date))
        offset_tmp = offset_tmp + timedelta(hours=offset)
        offset_time = offset_tmp.timetuple()

    else:
        offset_tmp = datetime.fromtimestamp(mktime(latest_date))
        offset_tmp = offset_tmp - timedelta(hours=hour_offset)
        offset_time = offset_tmp.timetuple()

    return offset_time


def download_chunk(args):
    global counter

    x, y, tile_count, latest = args
    url_format = "http://himawari8.nict.go.jp/img/D531106/{}d/{}/{}_{}_{}.png"

    with urlopen(url_format.format(tile_count, TILE_SIZE, strftime("%Y/%m/%d/%H%M%S", latest), x, y)) as tile_w:
        tiledata = tile_w.read()

    with counter.get_lock():
        counter.value += 1
        print("\rDownloading tiles: {}/{} completed".format(counter.value, tile_count * tile_count), end="", flush=True)
    return x, y, tiledata


def main():
    global counter

    # parse args
    arg_parser = argparse.ArgumentParser(description=__doc__,
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument("--width",
                            type=int,
                            default=1920,
                            dest="width",
                            help="Output image width in pixels")
    arg_parser.add_argument("--height",
                            type=int,
                            default=1200,
                            dest="height",
                            help="Output image height in pixels")
    arg_parser.add_argument("--hour-offset",
                            type=int,
                            default=None,
                            dest="hour_offset",
                            help="Define a hourly offset. Default calculates it automatically from your timezone.")
    arg_parser.add_argument("--xfce-displays",
                            default=("/backdrop/screen0/monitor0/image-path",
                                     "/backdrop/screen0/monitor0/workspace0/last-image"),
                            nargs="+",
                            dest="xfce_displays",
                            help="XFCE4 displays to change the background of")
    arg_parser.add_argument("-o",
                            "--output-file",
                            default=os.path.join(appdirs.user_cache_dir(appname="himawaripy",
                                                                        appauthor=False),
                                                 "latest.png"),
                            dest="output_file",
                            help="Image output file path")
    args = arg_parser.parse_args()

    if (args.hour_offset is not None) and (args.hour_offset < 0):
        exit("`hour_offset` must be greater than or equal to zero. I can't get future images of Earth for now.")

    print("Updating...")
    with urlopen("http://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json") as latest_json:
        latest = strptime(loads(latest_json.read().decode("utf-8"))["date"], "%Y-%m-%d %H:%M:%S")

    print("Latest version: {} GMT".format(strftime("%Y/%m/%d %H:%M:%S", latest)))
    if args.hour_offset != 0:
        requested_time = get_time_offset(latest, args.hour_offset)
        print("Offset version: {} GMT".format(strftime("%Y/%m/%d %H:%M:%S", requested_time)))
    else:
        requested_time = latest

    print()

    tile_count = math.ceil(max(args.width, args.height) / TILE_SIZE)
    for v in (4, 8, 16, 20):
        if tile_count <= v:
            tile_count = v
            break
    else:
        tile_count = 20
    png = Image.new('RGB', (TILE_SIZE * tile_count, TILE_SIZE * tile_count))

    counter = Value("i", 0)
    p = Pool(min(16, cpu_count() * tile_count))
    print("Downloading tiles: 0/{} completed".format(tile_count * tile_count), end="", flush=True)
    res = p.map(download_chunk, product(range(tile_count), range(tile_count), (tile_count,), (requested_time,)))

    for (x, y, tiledata) in res:
        tile = Image.open(BytesIO(tiledata))
        png.paste(tile, (TILE_SIZE * x, TILE_SIZE * y, TILE_SIZE * (x + 1), TILE_SIZE * (y + 1)))

    print("\nSaving as %ux%u to '%s'..." % (args.width, args.height, args.output_file))
    output_dir = os.path.dirname(args.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    png = png.resize((args.width, args.height), Image.LANCZOS)
    png.save(args.output_file, "PNG")

    if not set_background(args.output_file, xfce_displays=args.xfce_displays):
        exit("Your desktop environment '{}' is not supported.".format(get_desktop_environment()))

    print("Done!")

if __name__ == "__main__":
    main()
