from __future__ import annotations

import logging
import sys
from pathlib import Path

import bioread
import numpy as np
from bioread.biopac import Channel, Datafile


def all_same(items):
    return len(set(items)) < 2


def acq2raw(
    # Paths
    output_file: Path,
    # Channels
    channels: list[Channel],
    channel_indexes: list[int] = None,
) -> bool:
    """
    Writes a raw binary file from AcqKnowledge file

    Accepts channels to write.
    The Parameter 'channels' can be:
        - A path to '.acq' file
        - An AcqKnowledge Datafile from bioread
        - List of channels from an AcqKnowledge Datafile from bioread
    """

    def get_channels(channels) -> Datafile:
        if isinstance(channels, Path):
            return bioread.read(str(channels)).channels
        if isinstance(channels, Datafile):
            return channels.channels
        if isinstance(channels, list) and isinstance(channels[0], Channel):
            return channels
        logging.error(f"Given acq_file was not a Path, Datafile nor list of channels")
        sys.exit(1)

    channels = get_channels(channels)

    if channel_indexes is not None:
        channels = [channels[i] for i in channel_indexes]

    if len(channels):
        output_file.touch(exist_ok=True)

        byte_list = (
            np.array([channel.data for channel in channels], dtype="<f4")
            .flatten()
            .tobytes()
        )

        with output_file.open("wb") as raw:
            raw.write(byte_list)

        # Return writing went okay
        return True

    # Return writing did not happen
    return False
