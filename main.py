from __future__ import annotations

from pathlib import Path

import bioread

from error import true_or_exit

little_endian = True

channel_names = [
    "EMG",
    "Bit1",
    "Bit2",
    "Bit3",
    "Bit4",
    "Bit5",
    "Bit6",
    "Bit7",
    "Marker",
]
channel_units = [
    "mV",
    "Bit",
    "Bit",
    "Bit",
    "Bit",
    "Bit",
    "Bit",
    "Bit",
    "Bits",
]

def get_marker_info(marker):
    if marker in range(1, 9):
        return {"type": marker, "description": "Trial Start"}
    elif marker in range(11, 19):
        return {"type": marker, "description": "Trial End"}
    elif marker in range(21, 29):
        return {"type": marker, "description": "Feedback Start"}
    elif marker in range(31, 39):
        return {"type": marker, "description": "Feedback End"}
    elif marker == 41:
        return {"type": marker, "description": "Correct Response"}
    elif marker == 42:
        return {"type": marker, "description": "Incorrect Response"}
    elif marker == 43:
        return {"type": marker, "description": "No Response"}
    elif marker == 45:
        return {"type": marker, "description": "Target onset"}
    elif marker == 50:
        return {"type": marker, "description": "Practice Block Start"}
    elif marker in range(51, 60):
        return {"type": marker, "description": "Block Start"}
    elif marker == 60:
        return {"type": marker, "description": "Practice Block End"}
    elif marker in range(61, 70):
        return {"type": marker, "description": "Block End"}
    
    if marker - 70 > 0:
        practice_marker = get_marker_info(marker - 70)
        practice_marker["type"] = marker
        practice_marker["description"] = "Practice " + practice_marker["description"]
        return practice_marker
    else:
        return {"type": marker, "description": "UNKNOWN"}


marker_channel_index = 8

acq_folder = Path("acq_data")
templates_path = Path("templates")
# header_path, marker_path = (templates_path / "header_file.vhdr"), (
#    templates_path / "marker_file.vmrk"
# )
export_folder = Path("bva_data")

true_or_exit(
    acq_folder.exists() and acq_folder.is_dir(), "No 'acq_data' folder to work with"
)
true_or_exit(
    templates_path.exists() and acq_folder.is_dir(),
    "No templates to write for each file",
)
# true_or_exit(
#     header_path.exists() and header_path.is_file(),
#     "No template header file (.vhdr) exists",
# )

acq_files: list[Path] = []

for acq_file in acq_folder.iterdir():
    if acq_file.suffix == ".acq":
        acq_files.append(acq_file)

true_or_exit(len(acq_files), "No AcqKnowledge found in 'acq_data'")

export_folder.mkdir(exist_ok=True)

for acq_file in acq_files:
    acq = bioread.read(str(acq_files[0]))
    export_header = export_folder / acq_file.with_suffix(".vhdr").name
    export_marker = export_folder / acq_file.with_suffix(".vmrk").name

    """
    channel_infos = {}

    for i, channel in enumerate(acq.channels):
        name = channel_names[i] if channel_names else channel.name
        units = channel_units[i] if channel_units else channel.units
        channel_infos[f"Ch{i + 1}"] = f"{name},,1,{units}"

    header_data = {
        "[Common Infos]": {
            "DataFile": acq_file.name,
            "MarkerFile": export_marker.name,
            "DataFormat": "BINARY",
            "DataOrientation": "VECTORIZED",
            "DataType": "TIMEDOMAIN",
            "NumberOfChannels": len(acq.channels),
            "SamplingInterval": int(1000000 // acq.samples_per_second),
        },
        "[Binary Infos]": {
            "BinaryFormat": "IEEE_FLOAT_32",
            "UseBigEndianOrder": "NO" if little_endian else "YES",
        },
        "[Channel Infos]": channel_infos,
    }

    with export_header.open("wt") as header:
        header.write("Brain Vision Data Exchange Header File Version 1.0")
        header.write("\n")

        for head, settings in header_data.items():
            header.write("\n")
            header.write(head)
            header.write("\n")

            for key, value in settings.items():
                header.write(str(key))
                header.write("=")
                header.write(str(value))
                header.write("\n")
    """

    marker_channel = acq.channels[marker_channel_index]

    markers = []

    marker_found = False

    for position, data_point in enumerate(marker_channel.data):
        if marker_found:
            if data_point == 0.0:
                marker_found = False
                markers[-1]["points"] = position - markers[-1]["position"]
        else:
            if data_point > 0.0:
                marker_found = True
                marker = get_marker_info(int(data_point))
                markers.append({
                    "type": marker["type"],
                    "description": marker["description"],
                    "position": position,
                    "channel": 0,
                })

    marker_data = {
        "[Common Infos]": {
            "DataFile": acq_file.name,
        },
        "[Marker Infos]": {

        },
    }

    print(len(markers))

    for i in range(13):
        print(markers[i])

    break
