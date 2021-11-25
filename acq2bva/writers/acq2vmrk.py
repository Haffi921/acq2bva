from __future__ import annotations

import logging
from pathlib import Path

import bioread
from bioread.biopac import Channel

def create_marker_list(marker_channel: Channel, marker_map: dict[int, str], SMUDGE_LIMIT = 2):
    """
    Finds and returns a list of markers in a marker channel using a marker map.
    """
    def get_marker_description(marker: int, marker_map: dict[int, str]) -> str:
        for marker_range, description in marker_map.items():
            try:
                if marker in marker_range:
                    return description
            except TypeError:
                if marker == marker_range:
                    return description
        return ""

    markers = []
    marker = 0
    position = 0

    for pos, data in enumerate(marker_channel.data):
        if marker != data:
            if marker != 0:
                count = pos - position
                if count > SMUDGE_LIMIT:
                    markers.append({
                        "type": int(marker),
                        "description": get_marker_description(marker, marker_map),
                        "position": position,
                        "points": count,
                        "channel": 0,
                    })
            marker = data
            position = pos
    
    return markers

def generate_text(data_file: str, marker_list: list[dict]) -> str:
    """
    Generates vmrk file text
    """
    return_string = "BrainVision Data Exchange Marker File Version 1.0"

    return_string += "\n\n[Common Infos]"
    return_string += f"\nDataFile={data_file}"

    return_string += "\n\n[Marker Infos]"
    for i, marker in enumerate(marker_list, start=1):
        return_string += f"\nMk{i}="
        return_string += f"{marker['type']},{marker['description']},"
        return_string += f"{marker['position']},{marker['points']},{marker['channel']}"

    return return_string


def acq2vmrk(
    # Paths
    output_file: Path,
    data_file: str,
    # Markers
    marker_channel: Channel,
    marker_map: dict = {},
    expected_nr_markers: int = None,
) -> None:
    """
    Writes a '.vmrk' file for BrainVision Analyzer
    """
    marker_list = create_marker_list(marker_channel, marker_map)

    if expected_nr_markers is not None:
        if expected_nr_markers != len(marker_list):
            logging.warning(
                "Expected number of markers not matching up with marker list. "
                f"{expected_nr_markers} != {len(marker_list)}"
            )

    marker_text = generate_text(data_file, marker_list)

    with output_file.open("wt") as marker:
        marker.write(marker_text)