from __future__ import annotations

from pathlib import Path

import bioread
from bioread.biopac import Channel

from .acq2raw import acq2raw
from .acq2vhdr import acq2vhdr
from .acq2vmrk import acq2vmrk
from .error import true_or_exit


def acq2bva(
    output_folder: Path,
    acq_folder: Path = Path("acq_data"),
    channel_indexes=None,
    channel_names=None,
    channel_scales=None,
    channel_units=None,
    little_endian=True,
    write_markers=True,
    marker_channel_index=0,
    marker_map={},
    expected_nr_markers=None,
):
    true_or_exit(
        acq_folder.exists() and acq_folder.is_dir(), "No 'acq_data' folder to work with"
    )

    acq_files: list[Path] = []

    for acq_file in acq_folder.iterdir():
        if acq_file.suffix == ".acq":
            acq_files.append(acq_file)

    true_or_exit(len(acq_files), "No AcqKnowledge found in 'acq_data'")

    output_folder.mkdir(exist_ok=True)

    for acq_file in acq_files:
        acq = bioread.read(str(acq_file))

        output_file = (output_folder / acq_file.with_suffix(".dat").name).absolute()
        output_header = (output_folder / acq_file.with_suffix(".vhdr").name).absolute()

        if write_markers:
            output_marker = (
                output_folder / acq_file.with_suffix(".vmrk").name
            ).absolute()
        else:
            output_marker = Path("")

        writing_ok = acq2raw(
            output_file, acq.channels, little_endian, channel_indexes=channel_indexes
        )

        if writing_ok:
            acq2vhdr(
                output_header,
                output_file.name,
                acq.channels,
                channel_indexes=channel_indexes,
                marker_file=output_marker.name,
                names=channel_names,
                scales=channel_scales,
                units=channel_units,
                samples_per_second=acq.samples_per_second,
                little_endian=little_endian,
            )

            print(
                f"Wrote file {output_folder / output_file.name}: "
                f"{output_file.stat().st_size // pow(2, 20)} MB"
            )
            print(
                f"Wrote file {output_folder / output_header.name}: "
                f"{output_header.stat().st_size} B"
            )

            if write_markers:
                acq2vmrk(
                    output_marker,
                    output_file.name,
                    acq.channels[marker_channel_index],
                    marker_map,
                    expected_nr_markers=expected_nr_markers,
                )
                print(
                    f"Wrote file {output_folder / output_marker.name}: "
                    f"{output_marker.stat().st_size // pow(2, 10)} KB"
                )
