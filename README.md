# himawaripy
*Put near-realtime picture of Earth as your desktop background*

himawaripy is a Python 3 script that fetches near-realtime (10 minutes delayed)
picture of Earth as its taken by
[Himawari 8 (ひまわり8号)](https://en.wikipedia.org/wiki/Himawari_8) and sets it
as your desktop background.

Set a cronjob that runs in every 10 minutes to automatically get the
near-realtime picture of Earth.

## Supported Desktop Environments
### Tested
* Unity 7

### Not Tested
* GNOME 3
* MATE

### Not Supported
* [LXDE](http://wiki.lxde.org/en/LXDE_To_Do#PCManFM_.28file_manager.29)
* KDE

  Because I simply couldn't find a way to do it. Maybe [KDE API](http://api.kde.org/4.9-api/kdelibs-apidocs/plasma/html/classPlasma_1_1Wallpaper.html)?
* ... and all other desktop environments that are not mentioned above.

## Configuration
You can configure the level of detail, by modifying the script. You can set the
global variable `level` to `4`, `8`, `16`, or `20` to increase the quality (and
thus the file size as well). Please keep in mind that it will also take more
time to download the tiles.

## Installation
    cd ~
    git clone https://github.com/boramalper/himawaripy.git
    
    # configure
    cd ~/himawaripy
    vi himawaripy.py
    
    # test whether it's working
    ./himawaripy.py
    
    # set up a cronjob
    crontab -e
    # Add the line:
    # */10 * * * * /home/USERNAME/himawaripy/himawaripy.py
    
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
