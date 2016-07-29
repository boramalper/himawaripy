#!/bin/bash

RELATIVE_DIR=$(dirname $0)
BASE_DIR=$(realpath $RELATIVE_DIR)

sed -i 's/.config/config/g' $BASE_DIR/himawaripy.py
sed -i 's/.config/config/g' $BASE_DIR/utils.py
sed -i 's/.utils/utils/g' $BASE_DIR/himawaripy.py


echo "*/10 * * * * $BASE_DIR/himawaripy.py" | sudo tee /etc/cron.d/himawaripy
