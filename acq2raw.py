from __future__ import annotations

import logging
import sys
from pathlib import Path

import bioread
import numpy as np
from bioread.biopac import Channel, Datafile


def all_same(items):
    return len(set(items)) < 2


def get_channels(channels, channel_indexes) -> Datafile:
    if isinstance(channels, Path):
        ch = bioread.read(str(channels)).channels
        return [ch[i] for i in channel_indexes]
    if isinstance(channels, Datafile):
        return [channels.channels[i] for i in channel_indexes]
    if isinstance(channels, list) and isinstance(channels[0], Channel):
        return channels
    logging.error(f"Given acq_file was not a Path, Datafile nor list of channels")
    sys.exit(1)


def acq2raw(
    output_file: Path,
    channels: list[Channel],
    little_endian: bool = False,
    channel_indexes=None,
) -> Path:
    """
    Writes a raw binary file from AcqKnowledge file
    """
    channels = get_channels(channels, channel_indexes)
    nr_channels = len(channels)

    if nr_channels:
        output_file.touch(exist_ok=True)

        data_type = "<f4" if little_endian else ">f"
        byte_list = (
            np.array([channel.data for channel in channels], dtype=data_type)
            .flatten()
            .tobytes()
        )

        with output_file.open("wb") as raw:
            raw.write(byte_list)

        return True
    return False


if __name__ == "__main__":
    file = Path("acq_data/Feedback03.acq")
    output_path = Path("bva_data")

    acq2raw(file, output_path)
