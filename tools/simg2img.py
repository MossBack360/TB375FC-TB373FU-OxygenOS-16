from __future__ import annotations

import argparse
import struct
from pathlib import Path


MAGIC = 0xED26FF3A
RAW = 0xCAC1
FILL = 0xCAC2
DONT_CARE = 0xCAC3
CRC32 = 0xCAC4


def convert(source: Path, destination: Path) -> None:
    with source.open("rb") as src, destination.open("wb") as dst:
        header = src.read(28)
        magic, major, _minor, file_header_size, chunk_header_size, block_size, total_blocks, total_chunks, _checksum = struct.unpack(
            "<I4H4I", header
        )
        if magic != MAGIC or major != 1:
            raise ValueError("not an Android sparse image")
        src.seek(file_header_size)

        written_blocks = 0
        for _ in range(total_chunks):
            chunk_header = src.read(chunk_header_size)
            chunk_type, _reserved, chunk_blocks, total_size = struct.unpack("<2H2I", chunk_header[:12])
            data_size = total_size - chunk_header_size
            output_size = chunk_blocks * block_size

            if chunk_type == RAW:
                if data_size != output_size:
                    raise ValueError("invalid RAW chunk")
                remaining = data_size
                while remaining:
                    data = src.read(min(8 * 1024 * 1024, remaining))
                    if not data:
                        raise EOFError("truncated RAW chunk")
                    dst.write(data)
                    remaining -= len(data)
            elif chunk_type == FILL:
                if data_size != 4:
                    raise ValueError("invalid FILL chunk")
                fill = src.read(4)
                block = fill * (block_size // 4)
                for _ in range(chunk_blocks):
                    dst.write(block)
            elif chunk_type == DONT_CARE:
                if data_size:
                    src.seek(data_size, 1)
                dst.seek(output_size, 1)
            elif chunk_type == CRC32:
                src.seek(data_size, 1)
            else:
                raise ValueError(f"unknown chunk type 0x{chunk_type:04x}")
            written_blocks += chunk_blocks

        if written_blocks != total_blocks:
            raise ValueError(f"block count mismatch: {written_blocks} != {total_blocks}")
        dst.truncate(total_blocks * block_size)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    convert(args.source, args.destination)


if __name__ == "__main__":
    main()
