#!/usr/bin/env python3

from io import BytesIO
from json import loads
from time import strptime, strftime
from subprocess import call
from os import makedirs
from os.path import expanduser, split
from urllib.request import urlopen

from PIL import Image

from utils import get_desktop_environment, has_program
from multiprocessing import Pool, cpu_count, Value
from itertools import product

# Configuration
# =============

# Increases the quality and the size. Possible values: 4, 8, 16, 20
level = 4
width = 550
height = 550

# Path to the output file
output_file = expanduser("~/.himawari/himawari-latest.png")

# ==============================================================================
counter = None


def download_chunk(args):
    global counter

    x, y, latest = args
    url_format = "http://himawari8.nict.go.jp/img/D531106/{}d/{}/{}_{}_{}.png"

    with urlopen(url_format.format(level, width, strftime("%Y/%m/%d/%H%M%S", latest), x, y)) as tile_w:
        tiledata = tile_w.read()

    with counter.get_lock():
        counter.value += 1
        print("Downloading tiles: {}/{} completed".format(counter.value, level*level), end="\r", flush=True)
    return (x, y,tiledata)

def do_gnome():
    call(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", "file://" + output_file])
    call(["gsettings", "set", "org.gnome.desktop.background", "picture-options", "scaled"])
    call(["gsettings", "set", "org.gnome.desktop.background", "primary-color", "FFFFFF"])

def do_unity():
    # Because of a bug and stupid design of gsettings, see http://askubuntu.com/a/418521/388226
    call(["gsettings", "set", "org.gnome.desktop.background", "draw-background", "false"])
    do_gnome()

def do_mate():
    call(["gsettings", "set", "org.mate.background", "picture-filename", output_file])

def do_xfce4():
    call(["xfconf-query", "--channel", "xfce4-desktop", "--property", "/backdrop/screen0/monitor0/image-path", "--set", output_file])

def do_lxde():
    call(["display", "-window", "root", output_file])

def do_mac():
    call(["osascript","-e","tell application \"System Events\"\nset theDesktops to a reference to every desktop\nrepeat with aDesktop in theDesktops\nset the picture of aDesktop to \""+output_file+"\"\nend repeat\nend tell"])
    call(["killall","Dock"])

def do_feh():
    call(["feh", "--bg-max", output_file])

def main():
    global counter

    print("Updating...")
    with urlopen("http://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json") as latest_json:
        latest = strptime(loads(latest_json.read().decode("utf-8"))["date"], "%Y-%m-%d %H:%M:%S")

    print("Latest version: {} GMT\n".format(strftime("%Y/%m/%d %H:%M:%S", latest)))

    url_format = "http://himawari8.nict.go.jp/img/D531106/{}d/{}/{}_{}_{}.png"

    png = Image.new('RGB', (width*level, height*level))

    counter = Value("i", 0)
    p = Pool(cpu_count() * level)
    print("Downloading tiles: 0/{} completed".format(level*level), end="\r")
    res = p.map(download_chunk, product(range(level), range(level), (latest,)))

    for (x, y, tiledata) in res:
            tile = Image.open(BytesIO(tiledata))
            png.paste(tile, (width*x, height*y, width*(x+1), height*(y+1)))

    makedirs(split(output_file)[0], exist_ok=True)
    png.save(output_file, "PNG")

    supported_DEs = {
        "gnome": do_gnome,
        "unity": do_unity,
        "connamon": do_gnome,
        "pantheon": do_gnome,
        "gnome-classic": do_gnome,
        "mate": do_mate,
        "xfce4": do_xfce4,
        "lxde": do_lxde,
        "mac": do_mac,
    }

    de = get_desktop_environment()
    if de in supported_DEs:
        supported_DEs[de]()
    elif has_program("feh"):
        print("\nCouldn't detect your desktop environment ('{}'), but you have"
              "'feh' installed so we will use it.".format(de))
        do_feh()
    else:
        exit("Your desktop environment '{}' is not supported.".format(de))

    print("\nDone!\n")

if __name__ == "__main__":
    main()

