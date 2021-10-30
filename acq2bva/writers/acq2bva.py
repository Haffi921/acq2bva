from __future__ import annotations

from pathlib import Path

import bioread

from acq2bva.util.error import true_or_exit, true_or_fail
from acq2bva.writers.acq2raw import acq2raw
from acq2bva.writers.acq2vhdr import acq2vhdr
from acq2bva.writers.acq2vmrk import acq2vmrk


def acq2bva(
    # Paths
    output_folder: Path,
    acq: Path,
    # Channels
    channel_indexes: list[int] = None,
    channel_names: list[str] = None,
    channel_scales: list[int] = None,
    channel_units: list[str] = None,
    # Raw data
    little_endian: bool = True,
    # Markers
    write_markers: bool = False,
    marker_channel_index: int = None,
    marker_map: dict[int, str] = {},
    expected_nr_markers: int = None,
    # Other settings
    header_settings: dict = {},
) -> None:
    """
    Writes a raw '.dat' file and corresponding '.vhdr' file based on an AcqKnowledge file.

    Optional: Writes '.vmkr' file based on a marker channel
    """

    def get_file_size(file_path: Path):
        display_sizes = ["B", "KB", "MB", "GB"]
        file_size = file_path.stat().st_size
        for size in display_sizes:
            if file_size <= 1024:
                return f"{file_size} {size}"
            else:
                file_size //= 1024
        return f"{file_size} TB"

    def get_path_with_suffix(file_name: Path, suffix: str, directory: Path = None):
        new_file_name = file_name.with_suffix(suffix)
        if directory is not None:
            new_file_name = directory / new_file_name.name
        return new_file_name

    true_or_exit(
        acq.exists(),
        f"Error: {acq} does not exist",
    )

    output_file: Path = None
    output_header: Path = None
    output_marker: Path = None
    acq_files: list[Path] = []

    if acq.is_dir():
        for acq_file in acq.iterdir():
            if acq_file.suffix == ".acq":
                acq_files.append(acq_file)
    elif acq.is_file():
        acq_files.append(acq)

    true_or_exit(len(acq_files), "No AcqKnowledge file found")

    output_folder.mkdir(exist_ok=True)

    for acq_file in acq_files:
        acq_data = bioread.read(str(acq_file))

        output_file = get_path_with_suffix(acq_file, ".dat", output_folder)
        output_header = get_path_with_suffix(acq_file, ".vhdr", output_folder)
        if write_markers:
            output_marker = get_path_with_suffix(acq_file, ".vmrk", output_folder)

        writing_ok = acq2raw(
            # Paths
            output_file=output_file.absolute(),
            # Channels
            channels=acq_data.channels,
            channel_indexes=channel_indexes,
            # Raw data
            little_endian=little_endian,
        )

        if writing_ok:
            acq2vhdr(
                # Paths
                output_file=output_header.absolute(),
                data_file=output_file.name,
                # Channels
                channels=acq_data.channels,
                ch_names=channel_names,
                ch_scales=channel_scales,
                ch_units=channel_units,
                channel_indexes=channel_indexes,
                # Raw data
                samples_per_second=acq_data.samples_per_second,
                little_endian=little_endian,
                # Markers
                marker_file=output_marker.name if write_markers else None,
                # Other settings
                header_settings=header_settings,
            )

            print(f"Wrote file {output_file}: {get_file_size(output_file.absolute())}")
            print(
                f"Wrote file {output_header}: {get_file_size(output_header.absolute())}"
            )

            if write_markers:
                true_or_fail(
                    marker_channel_index is not None,
                    "To write markers, please indicate the marker channel index",
                )
                acq2vmrk(
                    # Paths
                    output_file=output_marker.absolute(),
                    data_file=output_file.name,
                    # Markers
                    marker_channel=acq_data.channels[marker_channel_index],
                    marker_map=marker_map,
                    expected_nr_markers=expected_nr_markers,
                )
                print(
                    f"Wrote file {output_marker}: {get_file_size(output_marker.absolute())}"
                )
