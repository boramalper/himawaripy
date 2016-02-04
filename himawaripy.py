#!/usr/bin/env python3

from io import BytesIO
from json import loads
from time import strptime, strftime
from os import system
from os.path import expanduser
from urllib.request import urlopen

from PIL import Image

from utils import get_desktop_environment

# Configuration
# =============

# Increases the quality and the size. Possible values: 4, 8, 16, 20
level = 4

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

    output_file = expanduser("~/.himawari-latest.png")
    png.save(output_file, "PNG")

    de = get_desktop_environment()
    if de in ["gnome", "unity", "cinnamon"]:
        # Because of a bug and stupid design of gsettings, see http://askubuntu.com/a/418521/388226
        system("gsettings set org.gnome.desktop.background draw-background false \
                && gsettings set org.gnome.desktop.background picture-uri file://" + output_file +
                " && gsettings set org.gnome.desktop.background picture-options scaled")
    elif de == "mate":
        system("gconftool-2 -type string -set /desktop/gnome/background/picture_filename \"{}\"".format(output_file))
    elif de == "xfce4":
        system("xfconf-query --channel xfce4-desktop --property /backdrop/screen0/monitor0/image-path --set " + output_file)
    else:
        exit("Your desktop environment '{}' is not supported.".format(de))

    print("Done!\n")

if __name__ == "__main__":
    main()
