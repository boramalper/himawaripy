from json import loads
from io import BytesIO
from urllib.request import urlopen
from time import strptime, strftime
from os import system
from os.path import expanduser
import argparse

from PIL import Image

# Configuration
# =============

# Increases the quality and the size. Possible values: 4, 8, 16, 20
level = 4 
# ==============================================================================

def main():
    # Setup argparser
    parser = argparse.ArgumentParser()
    parser.add_argument("--bgmethod", nargs=1, required=True, help="Method to set background, available: gnome, feh")
    args = parser.parse_args()
    
    if args.bgmethod[0] == "feh":
        bgsetstring = "feh --bg-max ~/.himawari-latest.png"
    elif args.bgmethod[0] == "gnome":
        # Because of a bug and stupid design of gsettings, see http://askubuntu.com/a/418521/388226
        bgsetstring = ("gsettings set org.gnome.desktop.background draw-background false \
                       && gsettings set org.gnome.desktop.background picture-uri file://"
                       + expanduser("~/.himawari-latest.png") + 
                      " && gsettings set org.gnome.desktop.background picture-options scaled")
    else:
        print("Unknown bgmethod, exiting.")
        exit(1)

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

    png.save(expanduser("~/.himawari-latest.png"), "PNG")
    
    system(bgsetstring)
    print("Done!\n")
    
if __name__ == "__main__":
    main()
