import os.path

import appdirs

# Increases the quality and the size. Possible values: 4, 8, 16, 20
level = 4

# Define a hourly offset or let the script calculate it depending on your timezone
# If auto_offset is True, then script will calculate your hour offset automatically depending on your location.
# If hour_offset is greater than 0, then script will use it.
# If both of the variables are set different than their default values below, then script will raise an error. Here,
# using the default values, script will put the realtime picture of Earth.
auto_offset = True
hour_offset = 0

# Path to the output file
output_file = os.path.join(appdirs.user_cache_dir(
    appname="himawaripy", appauthor=False), "latest.png")
# output_file = "/home/detavern/latest.png"

# margin offset(left upper right lower)
margin_offset = (0, 0, 0, 0)

# Check first tile of image if it's available
# If not("No Image"), it will try to get image 10 minutes earlier
# each retry will get image 10 minutes more eariler
max_retry_count = 3

# Xfce4 displays to change the background of
xfce_displays = ["/backdrop/screen0/monitor0/image-path",
                 "/backdrop/screen0/monitor0/workspace0/last-image"]
