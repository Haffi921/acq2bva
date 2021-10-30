# """Write the data from an AcqKnowledge file to BrainVision Analyzer format.
# """
from __future__ import annotations

import argparse, sys
import toml

from pathlib import Path

from acq2bva.__version__ import __version__
from acq2bva.writers.acq2bva import acq2bva

TOML_POSSIBILITES = ["settings.toml", "acq2bva.toml", "acq.toml", "bva.tpml"]

def main():
    settings = None
    use_settings = False

    for toml_file in map(Path, TOML_POSSIBILITES):
        if toml_file.is_file():
            settings = toml.load(toml_file)
            break
    

    try:
        if sys.argv[1] == "-s" or sys.argv[1] == "--settings":
            settings = toml.load(Path(sys.argv[2]))
    except:
        pass
    
    acq = None
    output_folder = None

    if settings is not None:
        acq_file = settings.get("acq_file")
        acq_folder = settings.get("acq_folder")
        output_folder = settings.get("output_folder")

        if output_folder and isinstance(output_folder, str):
            output_folder = Path(output_folder)
            if acq_file:
                if isinstance(acq_file, list):
                    acq = [Path(acq_item) for acq_item in acq_file]
                    use_settings = True
                elif isinstance(acq_file, str):
                    acq = Path(acq_file)
                    use_settings = True
            elif acq_folder and isinstance(acq_folder, str):
                acq = [Path(acq_folder)]
                use_settings = True
    else:
        settings = {}
    
    usage = """
    %(prog)s acq_file [acq_file ...] output_folder [optional args]
    %(prog)s acq_folder output_folder [optional args]
    %(prog)s [-s] toml_file [optional args] <if, and only if, the toml file specifies acq_file/folder and output_folder>
    %(prog)s <if, and only if, a toml file exists that specifies acq_file/folder and output_folder>
    %(prog)s [-h, --help]
    %(prog)s [-v, --version]
    """
    parser = argparse.ArgumentParser(
        prog="acq2bva",
        usage=usage,
        description="Write the data from an AcqKnowledge file to BrainVision Analyzer format",
    )
    parser.add_argument('-v', '--version', action="version", version='%(prog)s version ' + __version__)
    

    # Paths
    if not use_settings:
        parser.add_argument(
            "acq", nargs="+",
            type=Path,
            help="Folder or file(s) to convert",
        )
        parser.add_argument(
            "output_folder", action="store", metavar="output-folder",
            type=Path,
            help="Folder to store the BrainVision Analyzer files"
        )
    else:
        parser.add_argument("rest", nargs=argparse.REMAINDER)

    # Channels
    parser.add_argument(
        "-c", "--ci", "--channel-indexes", nargs="+", metavar="INDEX",
        type=int, dest="channel_indexes",
        help="Indexes of channels to include in raw file. Defaults to all channels.",
    )
    parser.add_argument(
        "-n", "--names", "--channel-names", nargs="+", metavar="NAME",
        type=str, dest="channel_names",
        help="Names of the channels. Defaults to names given by AcqKnowledge. "
        "Useful for renaming channels to something more readable."
    )
    parser.add_argument(
        "--sc", "--scales", "--channel-scales", nargs="+", metavar="SCALE",
        type=str, dest="channel_scales",
        help="Scales for each channel. Defaults to 1 for every channel."
    )
    parser.add_argument(
        "-u", "--units", "--channel-units", nargs="+", metavar="UNIT",
        type=str, dest="channel_units",
        help="Units for each channel. Defaults to units given by AcqKnowledge. "
        "Useful for fixing wrong units in recording."
    )

    # Raw data
    parser.add_argument(
        "--be", "--big-endian",
        dest="little_endian",
        help="Flag to write in big endian format. Defaults to writing in little endian."
    )
    
    # Markers
    parser.add_argument(
        "-m", "--markers", action="store_const", const=True,
        dest="write_markers",
        help="Flag to write a marker file based on a specific marker channel. "
        "If true, then marker channel (--mc) must be specified. "
        "Optionally, marker map file (--mf) can be specified to provide a description of each marker value. "
        "Please refer to the ReadMe or Github page for explanation of a marker map file. "
        "Additionally, expected number of markers (--em) can be specified and a warning will be displayed if "
        "number of markers found does not correspond to that value."
    )
    parser.add_argument(
        "--mc", "--marker-channel", action="store", metavar="INDEX",
        type=int, dest="marker_channel_index",
        help="A single channel index specifying which channel in the recording to scan for markers."
    )
    parser.add_argument(
        "--mf", "--marker-map-file", action="store", metavar="FILE",
        type=Path, dest="marker_map",
        help="Path of file specifying a marker mapping from the numerical value "
        "the description of that specific marker. For example, 1 -> 'Experiment start'. "
        "Please refer to the ReadMe or Github page for explanation of a marker map file."
    )
    parser.add_argument(
        "--em", "--expected-nr-markers", action="store", metavar="NR",
        type=int, dest="expected_nr_markers",
        help="Expected number of markers from each file. a warning will be displayed if "
        "number of markers found does not correspond with this value."
    )

    # Other settings
    parser.add_argument(
        "--hs", "--header-settings", action="store", metavar="FILE",
        type=Path, dest="header_settings",
        help="Toml file to specify settings for the '.vhdr' file. "
        "Any setting written in here will override settings configured automatically by this program."
    )

    # Other settings
    parser.add_argument(
        "-s", "--settings", action="store", metavar="FILE",
        type=Path, dest="settings",
        help="Toml file to any and all settings specified above. "
        "Any setting written in here will be overwritten by settings in the command line. "
        "Header settings can be specified here under [header_settings]."
    )

    args = parser.parse_args()

    if args.settings is not None:
        settings.update(args.settings)

    if not use_settings:
        acq: list[Path] = args.acq
        output_folder: Path = args.output_file
    elif len(args.rest) > 0:
        if len(args.rest) > 1:
            output_folder = Path(args.rest.pop())
        acq = list(map(Path, args.rest))
    
    for key, val in vars(args).items():
        if key not in settings or val is not None:
            settings[key] = val

    if settings["little_endian"] is None:
        settings["little_endian"] = True
    
    if settings["write_markers"] is None:
        settings["write_markers"] = False

    print(acq)
    print(output_folder)
    for key, val in settings.items():
        print(f"{key} = {val}")

    if len(acq) > 1:
        for acq_item in acq:
            if acq_item.is_dir():
                parser.print_usage()
                print("Error: Multiple AcqKnowledge directories given.")
                sys.exit(1)
    
    if isinstance(settings["channel_indexes"], int):
        settings["channel_indexes"] = [settings["channel_indexes"]]

    if settings["write_markers"]:
        if settings["marker_channel_index"] is None:
            parser.print_help()
            print("Error: Marker channel not specified.")
            sys.exit(1)
    
    if isinstance(settings["marker_map"], Path):
        print("Error: Marker map file has not been implemented yet.")
        sys.exit(1)
    elif isinstance(settings["marker_map"], dict):
        new_map = {}
        for marker, desc in settings["marker_map"].items():
            try:
                start, end = marker.split("-")
                new_map[range(int(start), int(end)+1)] = desc
            except:
                new_map[int(marker)] = desc
        settings["marker_map"] = new_map

    if isinstance(settings["header_settings"], Path):
        if not settings["header_settings"].exists():
            parser.print_usage()
            print("Error: Header settings file does not exist.")
            sys.exit(1)
        
        print("Not ready: Header settings file option has not been implemented yet.")
        sys.exit(1)

    for acq_item in acq:
        if not acq_item.exists():
            parser.print_usage()
            print(f"Error: {acq_item} is does not exist")
            sys.exit(1)
        
        acq2bva(
            output_folder=output_folder,
            acq=acq_item,
            channel_indexes=settings["channel_indexes"],
            channel_names=settings["channel_names"],
            channel_scales=settings["channel_scales"],
            channel_units=settings["channel_units"],
            little_endian=settings["little_endian"],
            write_markers=settings["write_markers"],
            marker_channel_index=settings["marker_channel_index"],
            marker_map=settings["marker_map"],
            expected_nr_markers=settings["expected_nr_markers"],
            header_settings=settings["header_settings"],
        )

if __name__ == '__main__':
    main()