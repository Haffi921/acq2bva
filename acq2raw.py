from __future__ import annotations

import logging
import sys
from datetime import timedelta
from pathlib import Path
from time import perf_counter

import bioread
import numpy as np
from bioread.biopac import Channel, Datafile

logging.basicConfig(level=logging.DEBUG)


def all_same(items):
    return len(set(items)) < 2


def get_acq_instance(file) -> Datafile:
    if isinstance(file, Path):
        return bioread.read(str(file))
    if isinstance(file, Datafile):
        return file
    logging.error(f"Given acq_file was not a DataFile nor Path")
    sys.exit(1)


class Timer:
    def __init__(self):
        self.t0 = perf_counter()

    def stop(self, msg=""):
        t = timedelta(seconds=perf_counter() - self.t0)
        logging.info(f"{msg}{t}")


def acq2raw(
    acq_file: Path,
    output_path: Path = None,
    little_endian: bool = False,
    channel_indexes=None,
):
    """
    Writes a raw binary file from AcqKnowledge file
    """
    raw_folder = Path(output_path) if output_path else acq_file.parents[0]
    raw_file = (raw_folder / acq_file.with_suffix(".dat").name).absolute()

    acq = get_acq_instance(acq_file)

    if channel_indexes is not None:
        channels: list[Channel] = [acq.channels[i] for i in channel_indexes]
    else:
        channels: list[Channel] = acq.channels

    nr_channels = len(channels)

    if nr_channels:
        point_counts = [channel.point_count for channel in channels]
        total_points = sum(point_counts)

        raw_folder.mkdir(exist_ok=True)
        raw_file.touch(exist_ok=True)

        t = Timer()

        data_type = "<f4" if little_endian else ">f"
        byte_list = (
            np.array([channel.data for channel in channels], dtype=data_type)
            .flatten()
            .tobytes()
        )

        with raw_file.open("wb") as raw:
            raw.write(byte_list)

        t.stop("Finished writing raw file. Elapsed time: ")

        logging.info(
            f"Wrote {total_points} data points for {nr_channels} channels, total of {raw_file.stat().st_size // pow(2, 20)} MB"
        )


if __name__ == "__main__":
    file = Path("acq_data/Feedback03.acq")
    output_path = Path("bva_data")

    acq2raw(file, output_path)
