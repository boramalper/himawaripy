#!/usr/bin/env python3

from io import BytesIO
from json import loads
from time import strptime, strftime
from subprocess import call
from os import makedirs
from os.path import expanduser, split
from urllib.request import urlopen

from PIL import Image

from utils import get_desktop_environment

# Configuration
# =============

# Increases the quality and the size. Possible values: 4, 8, 16, 20
level = 4

# Path to the output file
output_file = expanduser("~/.himawari/himawari-latest.png")

# ==============================================================================

def main():
    width = 550
    height = 550

    print("Updating...")
    with urlopen("http://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json") as latest_json:
        latest = strptime(loads(latest_json.read().decode("utf-8"))["date"], "%Y-%m-%d %H:%M:%S")

    print("Latest version: {} GMT\n".format(strftime("%Y/%m/%d/%H:%M:%S", latest)))

    url_format = "http://himawari8.nict.go.jp/img/D531106/{}d/{}/{}_{}_{}.png"

    png = Image.new('RGB', (width*level, height*level))

    print("Downloading tiles: 0/{} completed".format(level*level), end="\r")
    for x in range(level):
        for y in range(level):
            with urlopen(url_format.format(level, width, strftime("%Y/%m/%d/%H%M%S", latest), x, y)) as tile_w:
                tiledata = tile_w.read()

            tile = Image.open(BytesIO(tiledata))
            png.paste(tile, (width*x, height*y, width*(x+1), height*(y+1)))

            print("Downloading tiles: {}/{} completed".format(x*level + y + 1, level*level), end="\r")
    print("\nDownloaded\n")

    makedirs(split(output_file)[0], exist_ok=True)
    png.save(output_file, "PNG")

    de = get_desktop_environment()
    if de in ["gnome", "unity", "cinnamon"]:
        # Because of a bug and stupid design of gsettings, see http://askubuntu.com/a/418521/388226
        if de == "unity":
            call(["gsettings", "set", "org.gnome.desktop.background", "draw-background", "false"])
        call(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", "file://" + output_file])
        call(["gsettings", "set", "org.gnome.desktop.background", "picture-options", "scaled"])
    elif de == "mate":
        call(["gconftool-2", "-type", "string", "-set", "/desktop/gnome/background/picture_filename", '"{}"'.format(output_file)])
    elif de == "xfce4":
        call(["xfconf-query", "--channel", "xfce4-desktop", "--property", "/backdrop/screen0/monitor0/image-path", "--set", output_file])
    elif de == "lxde":
        call(["display", "-window", "root", output_file])
    elif de == "mac":
        call(["osascript","-e","tell application \"System Events\"\nset theDesktops to a reference to every desktop\nrepeat with aDesktop in theDesktops\nset the picture of aDesktop to \""+output_file+"\"\nend repeat\nend tell"])
    else:
        exit("Your desktop environment '{}' is not supported.".format(de))

    print("Done!\n")

if __name__ == "__main__":
    main()
