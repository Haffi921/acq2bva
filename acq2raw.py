from __future__ import annotations
import os

import struct, sys, logging, tempfile, threading, time, multiprocessing
from pathlib import Path
logging.basicConfig(level=logging.DEBUG)

from bioread import read

from error import true_or_fail
from progress_bar import updt

def float2bin_ieee32bit(number: float, little_endian: bool = False) -> int:
    endianness = "f" if little_endian else "!f"
    bin_rep = ""
    for c in struct.pack(endianness, number):
        bin_rep += bin(c).replace("0b", "").rjust(8, "0")
    return int(bin_rep)

def float2IEEE(number: float, little_endian: bool = False) -> list[bytes]:
    endianness = "<f" if little_endian else ">f"
    return [c.to_bytes(length=1, byteorder="little") for c in struct.pack(endianness, number)]

def all_same(items):
    return len(set(items)) < 2

class Counter:
    count = 0
    max = 0

    @classmethod
    def set_max(cls, n):
        cls.max = n

    @classmethod
    def update(cls):
        cls.count += 1
        updt(cls.max, cls.count)

def channel_data_to_bytes(return_data, nr, channel_data, little_endian):
    logging.debug(f"Starting with channel {nr}")
    data = []
    for data_point in channel_data:
        for byte in float2IEEE(data_point, little_endian=little_endian):
            data.append(byte)
    return_data[nr] = data
    logging.debug(f"Finishing with channel {nr}")

def channel_bytes_to_temp(return_data, nr):
    logging.debug(f"Starting with channel {nr}")
    data = return_data[nr]
    file = tempfile.TemporaryFile("wb")
    for data_point in data:
        file.write(data_point)
    file.seek(0)
    return_data[nr] = file
    logging.debug(f"Finishing with channel {nr}")

def acq2raw(
    file_path: Path,
    output_path: Path = None,
    little_endian: bool = False,
    interweaved: bool = False,
    channel_indexes = None):
    """
    Writes a raw binary file from AcqKnowledge file
    """
    raw_folder = Path(output_path) if output_path else file_path.parents[0]
    raw_file = (raw_folder / file_path.with_suffix(".dat").name).absolute()

    acq = read(str(file_path))
    
    if channel_indexes is not None:
        channels = [acq.channels[i] for i in channel_indexes]
    else:
        channels = acq.channels

    nr_channels = len(channels)
    frequency_devisors = [channel.frequency_divider for channel in channels]
    point_counts = []

    if nr_channels:
        for channel in channels:
            point_counts.append(channel.point_count)

        total_points = sum(point_counts)

        raw_folder.mkdir(exist_ok=True)
        raw_file.touch(exist_ok=True)
        """
        with raw_file.open("wb") as raw:
            if interweaved:
                point = 0
                for i in range(max(point_counts)):
                    for channel, divisor in zip(channels, frequency_devisors):
                        if i % divisor == 0:
                            point += 1
                            updt(total_points, point)
                            for byte in float2IEEE(channel.data[int(i / divisor)]):
                                raw.write(byte)
            else:
        """
        """
        point = 0
            
        def write_channel_data(file, channel_data):
            logging.debug("Task started")
            for data_point in channel_data:
                for byte in float2IEEE(data_point, little_endian=little_endian):
                    file.write(byte)
                with threading.Lock():
                    nonlocal point
                    point += 1
                    updt(total_points, point)
            file.seek(0)

        file_parts = []
        threads: list[threading.Thread] = []
        for i, channel in enumerate(channels):
            new_file = tempfile.TemporaryFile()
            new_thread = threading.Thread(target=write_channel_data, args=(new_file, channel.data), daemon=True)
            file_parts.append(new_file)
            threads.append(new_thread)
            new_thread.start()
            logging.debug(f"Thread {i} started")
        
        for thread in threads:
            thread.join()
        
            for file in file_parts:
                raw.write(file.read())
                file.close()
                
                """
        manager = multiprocessing.Manager()
        file_parts = manager.dict()
        
        t0 = time.perf_counter()
        processes: list[multiprocessing.Process] = []
        for i, channel in enumerate(channels):
            new_p = multiprocessing.Process(target=channel_data_to_bytes, args=(file_parts, i, channel.data, little_endian))
            processes.append(new_p)
            new_p.start()

        for proc in processes:
            proc.join()

        t1 = time.perf_counter()
        logging.debug(f"Finished transcribing bytes {(t1 - t0) / 60}")

        t0 = time.perf_counter()
        processes: list[multiprocessing.Process] = []
        for channel_nr in range(nr_channels):
            new_p = multiprocessing.Process(target=channel_bytes_to_temp, args=(file_parts, channel_nr))
            processes.append(new_p)
            new_p.start()

        for proc in processes:
            new_p.join()

        with raw_file.open("wb") as raw:
            for channel_nr in range(nr_channels):
                for file_part in file_parts[channel_nr]:
                    raw.write(file_part.read())
                    file_part.close()
                updt(nr_channels, channel_nr)
                    
        t1 = time.perf_counter()
        logging.debug(f"Finished writing bytes {(t1 - t0) / 60}")
        """
        for process in processes:
            process.join()
        
        with raw_file.open("wb") as raw:
            for file in file_parts:
                raw.write(file.read())
                file.close()

        t0 = time.perf_counter()
        with raw_file.open("wb") as raw:
            point = 0
            for channel in channels:
                for data_point in channel.data:
                    point += 1
                    updt(total_points, point)
                    for byte in float2IEEE(data_point, little_endian=little_endian):
                        raw.write(byte)
        t1 = time.perf_counter()
        """

                
        if all_same(point_counts):
            logging.debug(f"Wrote {point_counts[0]} data points for {nr_channels} channels")
        else:
            logging.debug(f"Wrote data for {nr_channels} channels:")
            for channel_nr, count in enumerate(point_counts):
                logging.debug(f"{channel_nr} - {count} data points")

if __name__ == "__main__":
    file = Path("acq_data/Feedback03.acq")
    output_path = Path("raw")

    acq2raw(file, output_path)