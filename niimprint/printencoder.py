import logging
import struct
import sys

import PIL.Image as Image
import PIL.ImageOps as ImageOps

from niimbotpacket import NiimbotPacket

logger = logging.getLogger(__name__)


def countbitsofbytes(bytes):
    if sys.version_info.minor >= 10:
        return int.from_bytes(bytes, "big").bit_count()
    else:
        n = int.from_bytes(bytes, "big")
        # https://stackoverflow.com/a/9830282
        n = (n & 0x55555555) + ((n & 0xAAAAAAAA) >> 1)
        n = (n & 0x33333333) + ((n & 0xCCCCCCCC) >> 2)
        n = (n & 0x0F0F0F0F) + ((n & 0xF0F0F0F0) >> 4)
        n = (n & 0x00FF00FF) + ((n & 0xFF00FF00) >> 8)
        n = (n & 0x0000FFFF) + ((n & 0xFFFF0000) >> 16)
        return n


def naive_encoder(img: Image.Image):
    img_data = ImageOps.invert(img.convert("L")).convert("1").tobytes()

    line_width = img.width // 8
    checksum_bytes = 3
    checksum_chunks = line_width // 3

    for line in range(img.height):
        line_data = img_data[line * line_width : (line + 1) * line_width]
        checksum = (
            countbitsofbytes(
                line_data[byte_idx * checksum_chunks : (byte_idx + 1) * checksum_chunks]
            )
            for byte_idx in range(checksum_bytes)
        )
        # create four byte header with the following format:
        # |   Line number    | Checksum Chunk 0 | Checksum Chunk 2 | Checksum Chunk 3 |       0x01       |
        header = struct.pack(">H3BB", line, *checksum, 1)
        logger.info(f"header bytes: {header}")
        yield NiimbotPacket(0x85, header + line_data)
