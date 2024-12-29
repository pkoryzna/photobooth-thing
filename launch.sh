#!/usr/bin/env bash


while true; do
    (
    source $HOME/photobooth-thing/env/bin/activate
    set -xeuo pipefail
    export DISPLAY=:0
    unclutter -idle 0 &
    cd $HOME/photobooth-thing/
    python3 -m one_bit_photo.main
    )
done