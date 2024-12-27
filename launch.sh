#!/usr/bin/env bash
set -xeuo pipefail


while true; do
    (
    source $HOME/photobooth-thing/env/bin/activate
    export DISPLAY=:0
#    unclutter
    cd $HOME/photobooth-thing/
    python3 -m one_bit_photo.main
    )
done