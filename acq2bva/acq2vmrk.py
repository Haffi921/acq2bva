from __future__ import annotations

from pathlib import Path

import bioread
from bioread.biopac import Channel


def get_marker_description(marker: int, marker_map: dict) -> str:
    for marker_range, description in marker_map.items():
        if marker in marker_range:
            return description


def find_all_markers(marker_channel: Channel, marker_map: dict) -> list[dict]:
    def mark_hit():
        markers.append(
            {
                "type": marker,
                "description": get_marker_description(marker, marker_map),
                "position": position,
                "channel": 0,
            }
        )

    def finish_hit():
        markers[-1]["points"] = position - markers[-1]["position"]

    markers = []
    marker_hit = False
    marker = 0

    for position, data_point in enumerate(marker_channel.data):
        if marker_hit:
            if data_point <= 0.0:
                finish_hit()
                marker_hit = False
        else:
            if data_point > 0.0:
                marker = int(data_point)
                mark_hit()
                marker_hit = True

    return markers


def generate_text(data_file: str, marker_list: list[dict]) -> str:
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
    output_file: Path, data_file: str, marker_channel: Channel, marker_map: dict
) -> None:
    marker_list = find_all_markers(marker_channel, marker_map)
    marker_text = generate_text(data_file, marker_list)

    with output_file.open("wt") as marker:
        marker.write(marker_text)


if __name__ == "__main__":
    marker_map = {
        range(1, 9): "Trial Start",
        range(11, 19): "Trial End",
        range(21, 29): "Feedback Start",
        range(31, 39): "Feedback End",
        (41,): "Correct Response",
        (42,): "Incorrect Response",
        (43,): "No Response",
        (45,): "Target Onset",
        range(51, 59): "Block Start",
        range(61, 69): "Block End",
        range(71, 79): "Practice Trial Start",
        range(81, 89): "Practice Trial End",
        range(91, 99): "Practice Feedback Start",
        range(101, 109): "Practice Feedback End",
        (50,): "Practice Block Start",
        (60,): "Practice Block End",
    }

    data_file = Path("Feedback03.dat")
    marker_file = data_file.with_suffix(".vmrk")
    acq = bioread.read(str(Path("acq_data/Feedback03.acq")))

    marker_list = find_all_markers(acq.channels[-1], marker_map)

    print(generate_text(data_file, marker_list))