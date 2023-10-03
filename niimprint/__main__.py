import argparse
import printerclient
import printencoder

from PIL import Image
import time

import logging

# import math
# mm_to_px = lambda x: math.ceil(x / 25.4 * 203)
# px_to_mm = lambda x: math.ceil(x / 25.4 * 203)

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level=logging.INFO,
    )
    parser = argparse.ArgumentParser(description="Niimbot printer client")
    parser.add_argument(
        "-a", "--address", required=True, help="MAC address of target device"
    )
    parser.add_argument("--no-check", action="store_true", help="Skips image check")
    parser.add_argument(
        "-d", "--density", type=int, default=2, help="Printer density (1~3)"
    )
    parser.add_argument("-t", "--type", type=int, default=1, help="Label type (1~3)")
    parser.add_argument(
        "-n", "--quantity", type=int, default=1, help="Number of copies"
    )
    parser.add_argument("image", help="PIL supported image file")
    args = parser.parse_args()

    img = Image.open(args.image)
    # if img.width / img.height > 1:
    #     # rotate clockwise 90deg, upper line (left line) prints first.
    #     img = img.transpose(Image.ROTATE_270)

    if img.width > 400 and img.height < 400:
        img = img.transpose(Image.ROTATE_270)

    assert (img.width % 8 == 0) and (
        (img.width / 8) % 3 == 0
    ), "The image's width must be divisible by 8, and that divisor must be divisble by 3"

    printer = printerclient.PrinterClient(args.address)
    printer.set_label_type(args.type)
    printer.set_label_density(args.density)

    printer.start_print()
    printer.allow_print_clear()
    printer.start_page_print()
    printer.set_dimension(img.height, img.width)
    printer.set_quantity(args.quantity)
    for pkt in printencoder.naive_encoder(img):
        printer._send(pkt)
    printer.end_page_print()
    # while (a := printer.get_print_status())["page"] != args.quantity:
    #     print(a)
    #     time.sleep(0.1)
    printer.end_print()
