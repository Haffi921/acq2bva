import logging
from pathlib import Path

from acq2bva import acq2bva

logging.basicConfig(level=logging.DEBUG)


channel_names = [
    "EMG",
    "Marker",
]
channel_units = [
    "mV",
    "Bits",
]

marker_map = {
    range(1, 9): "Trial Start",
    range(11, 19): "Trial End",
    range(21, 29): "Feedback Start",
    range(31, 39): "Feedback End",
    41: "Correct Response",
    42: "Incorrect Response",
    43: "No Response",
    45: "Target Onset",
    range(51, 59): "Block Start",
    range(61, 69): "Block End",
    range(71, 79): "Practice Trial Start",
    range(81, 89): "Practice Trial End",
    range(91, 99): "Practice Feedback Start",
    range(101, 109): "Practice Feedback End",
    50: "Practice Block Start",
    60: "Practice Block End",
}


if __name__ == "__main__":
    dir = Path(__file__).parent.resolve()
    acq2bva(
        dir / "bva_data",
        dir / "acq_data",
        channel_indexes=[0],
        channel_names=["EMG"],
        channel_units=["mV"],
        write_markers=True,
        marker_channel_index=8,
        marker_map=marker_map,
        expected_nr_markers=4818,
    )
