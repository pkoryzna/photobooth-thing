cd $HOME/photobooth-thing/
source $HOME/photobooth-thing/env/bin/activate
brother_ql --backend pyusb --model QL-720NW --printer usb://0x04f9:0x2044 print --label 62 pixel.png --no-cut

