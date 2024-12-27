import sys

import brother_ql.labels
from brother_ql import BrotherQLRaster
from brother_ql.backends.pyusb import list_available_devices
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send

def print_image(images, label_type, printer_instance):
    raster = BrotherQLRaster("QL-720NW")
    convert(raster, images, label=label_type, cut=True, dither=False)
    send(raster.data, printer_identifier=printer_instance, backend_identifier="pyusb", blocking=True)


def discover_printer():
    printers = list_available_devices()
    print(f"Found printers: {printers}", file=sys.stderr)
    if not printers:
        raise IndexError("No printer found!")
        # return None
    printer = printers[0]["instance"]
    return printer
