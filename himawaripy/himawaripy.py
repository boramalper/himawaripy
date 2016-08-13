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

from PIL import Image, ImageChops
from pytz import timezone
from tzlocal import get_localzone

from .utils import set_background, get_desktop_environment
from .config import level, output_file, auto_offset, hour_offset, margin_offset, max_retry_count

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


def download_chunk_once(args):
    x, y, latest = args
    url_format = "http://himawari8.nict.go.jp/img/D531106/{}d/{}/{}_{}_{}.png"

    with urlopen(url_format.format(level, width, strftime(
                 "%Y/%m/%d/%H%M%S", latest), x, y)) as tile_w:
        tiledata = tile_w.read()
    print("Downloading one tile completed")
    return x, y, tiledata


def add_margin(png):
    back_png = Image.new('RGB', (
        png.width + margin_offset[0] + margin_offset[2],
        png.height + margin_offset[1] + margin_offset[3]
    ))
    box = (margin_offset[0], margin_offset[1],
           margin_offset[0] + png.width, margin_offset[1] + png.height)
    back_png.paste(png, box)
    return back_png


def equal_image(im1, im2):
    return ImageChops.difference(im1, im2).getbbox() is None


def check_chunk_by_time(requested_time, delta=10, max_retry=max_retry_count):
    '''
    check first chunk of default level by certain time
    return latest time with normal image
    '''

    pattern = Image.open(r'himawaripy/src/no-image.png')
    print('Image check ...')
    for i in range(max_retry):
        tile = Image.open(BytesIO(
            download_chunk_once((0, 0, requested_time))[-1]))
        if equal_image(pattern, tile) is False:
            print('Version: {} GMT available\n'.format(
                strftime("%Y/%m/%d %H:%M:%S", requested_time)))
            break
        print('No image at version: {} GMT'.format(
            strftime("%Y/%m/%d %H:%M:%S", requested_time)))
        requested_tmp = datetime.fromtimestamp(mktime(requested_time))
        requested_tmp = requested_tmp - timedelta(minutes=delta)
        requested_time = requested_tmp.timetuple()
        print('Try earlier version: {} GMT (delta:{}, count:{})\n'.format(
            strftime("%Y/%m/%d %H:%M:%S", requested_time), delta, i + 1))
    else:
        print('Retry times reached maximum!')
        exit()
    return requested_time


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
    requested_time = check_chunk_by_time(requested_time)
    p = Pool(cpu_count() * level)
    print("Downloading tiles: 0/{} completed".format(level * level), end="", flush=True)
    res = p.map(download_chunk, product(range(level), range(level), (requested_time,)))

    for (x, y, tiledata) in res:
        tile = Image.open(BytesIO(tiledata))
        png.paste(tile, (width * x, height * y, width * (x + 1), height * (y + 1)))

    print("\nAdd margin (left:{} upper:{} right:{} lower:{})".format(*margin_offset))
    png = add_margin(png)

    print("Saving to '%s'..." % (output_file))
    makedirs(dirname(output_file), exist_ok=True)
    png.save(output_file, "PNG")

    if not set_background(output_file):
        exit("Your desktop environment '{}' is not supported.".format(get_desktop_environment()))

    print("Done!")

if __name__ == "__main__":
    main()
