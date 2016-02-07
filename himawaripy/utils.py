import os
import sys
import subprocess

from .config import xfce_displays


def set_background(file_path):
    de = get_desktop_environment()

    if de in ["gnome", "unity", "cinnamon", "pantheon", "gnome-classic"]:
        # Because of a bug and stupid design of gsettings, see http://askubuntu.com/a/418521/388226
        if de == "unity":
            subprocess.call(["gsettings", "set", "org.gnome.desktop.background", "draw-background", "false"])
        subprocess.call(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", "file://" + file_path])
        subprocess.call(["gsettings", "set", "org.gnome.desktop.background", "picture-options", "scaled"])
        subprocess.call(["gsettings", "set", "org.gnome.desktop.background", "primary-color", "FFFFFF"])
    elif de == "mate":
        subprocess.call(["gsettings", "set", "org.mate.background", "picture-filename", file_path])
    elif de == "xfce4":
        for display in xfce_displays:
            subprocess.call(["xfconf-query", "--channel", "xfce4-desktop", "--property", display, "--set", file_path])
    elif de == "lxde":
        subprocess.call(["pcmanfm", "--set-wallpaper", file_path, "--wallpaper-mode=fit", ])
    elif de == "mac":
        subprocess.call(["osascript", "-e", 'tell application "System Events"\n'
                         'set theDesktops to a reference to every desktop\n'
                         'repeat with aDesktop in theDesktops\n'
                         'set the picture of aDesktop to \"' + file_path + '"\nend repeat\nend tell'])
        subprocess.call(["killall", "Dock"])
    elif has_program("feh"):
        print("\nCouldn't detect your desktop environment ('{}'), but you have"
              "'feh' installed so we will use it.".format(de))
        os.environ['DISPLAY'] = ':0'
        subprocess.call(["feh", "--bg-max", file_path])
    elif has_program("nitrogen"):
        print("\nCouldn't detect your desktop environment ('{}'), but you have "
              "'nitrogen' installed so we will use it.".format(de))
        os.environ["DISPLAY"] = ':0'
        subprocess.call(["nitrogen", "--restore"])
    else:
        return False

    return True


# http://stackoverflow.com/a/21213358/4466589
def get_desktop_environment():
    # From http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=1139057
    if sys.platform in ["win32", "cygwin"]:
        return "windows"
    elif sys.platform == "darwin":
        return "mac"
    else: # Most likely either a POSIX system or something not much common
        desktop_session = os.environ.get("DESKTOP_SESSION")
        if desktop_session is not None: # Easier to match if we don't have to deal with caracter cases
            desktop_session = desktop_session.lower()
            if desktop_session in ["gnome", "unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox",
                                   "blackbox", "openbox", "icewm", "jwm", "afterstep","trinity", "kde", "pantheon",
                                   "gnome-classic"]:
                return desktop_session
            ## Special cases ##
            # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if using LXDE.
            # There is no guarantee that they will not do the same with the other desktop environments.
            elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
                return "xfce4"
            elif desktop_session.startswith("ubuntu"):
                return "unity"
            elif desktop_session.startswith("lubuntu"):
                return "lxde"
            elif desktop_session.startswith("kubuntu"):
                return "kde"
            elif desktop_session.startswith("razor"): # e.g. razorkwin
                return "razor-qt"
            elif desktop_session.startswith("wmaker"): # e.g. wmaker-common
                return "windowmaker"
        if os.environ.get('KDE_FULL_SESSION') == 'true':
            return "kde"
        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            if "deprecated" not in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                return "gnome2"
        # From http://ubuntuforums.org/showthread.php?t=652320
        elif is_running("xfce-mcs-manage"):
            return "xfce4"
        elif is_running("ksmserver"):
            return "kde"

    # We couldn't detect it so far, so let's try one last time
    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP")
    if current_desktop:
        current_desktop = current_desktop.lower()
        if current_desktop in ["gnome", "unity", "kde", "gnome-classic", "mate"]:
            return current_desktop

        # Special Cases
        elif current_desktop == "xfce":
            return "xfce4"
        elif current_desktop == "x-cinnamon":
            return "cinnamon"

    return "unknown"


def has_program(program):
    try:
        subprocess.check_output(["which", "--", program])
        return True
    except subprocess.CalledProcessError:
        return False


def is_running(process):
    try:
        subprocess.check_output (["pidof", "--", process])
        return True
    except subprocess.CalledProcessError:
        return False
