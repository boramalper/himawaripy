# himawaripy
*Put near-realtime picture of Earth as your desktop background*

himawaripy is a Python 3 script that fetches near-realtime (10 minutes delayed)
picture of Earth as its taken by
[Himawari 8 (ひまわり8号)](https://en.wikipedia.org/wiki/Himawari_8) and sets it
as your desktop background.

Set a cronjob that runs in every 10 minutes to automatically get the
near-realtime picture of Earth.

Tested on Ubuntu 15.10.

## Configuration
You can configure the level of detail, by modifying the script. You can set the
global variable `level` to `4`, `8`, `16`, or `20` to increase the quality (and
thus the file size as well). Please keep in mind that it will also take more
time to download the tiles.

You also need to choose the method, how to set your background image. Either set the background via the Gnome shell (*gnome*) or via the feh tool (*feh*). In order to be able to use feh, you need to install prior usage.
## Installation
    cd ~
    git clone https://github.com/boramalper/himawaripy.git
    
    # configure
    cd ~/himawaripy
    vi himawaripy.py
    
    # test whether it's working
    python3 himawaripy.py --bgmethod gnome
    
    # set up a cronjob
    crontab -e
    # Add the line:
    # */10 * * * * python3 /home/USERNAME/himawaripy/himawaripy.py --bgmethod gnome
    
## Example
![Earth, as 2016/02/04/13:30:00 GMT](http://i.imgur.com/4XA6WaM.jpg)
    
## Attributions
Thanks to *[MichaelPote](https://github.com/MichaelPote)* for the [initial
implementation](https://gist.github.com/MichaelPote/92fa6e65eacf26219022) using
Powershell Script.

Thanks to *[Charlie Loyd](https://github.com/celoyd)* for image processing logic
([hi8-fetch.py](https://gist.github.com/celoyd/39c53f824daef7d363db)).

Obviously, thanks to the Japan Meteorological Agency for opening these pictures
to public.
