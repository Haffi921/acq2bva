# """Write the data from an AcqKnowledge file to BrainVision Analyzer format.
# """
from __future__ import annotations

import argparse, sys


from pathlib import Path

from acq2bva.__version__ import __version__
from acq2bva.writers.acq2bva import acq2bva

def main():
    usage = """
    %(prog)s acq_file [acq_file ...] output_folder [optional arguments]
    %(prog)s acq_folder output_folder [optional arguments]
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
        "-s", "--scales", "--channel-scales", nargs="+", metavar="SCALE",
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
        "--be", "--big-endian", action="store_false",
        dest="little_endian",
        help="Flag to write in big endian format. Defaults to writing in little endian."
    )
    
    # Markers
    parser.add_argument(
        "-m", "--markers", action="store_true",
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

    args = parser.parse_args()

    acq: list[Path] = args.acq

    if len(acq) > 1:
        for acq_item in acq:
            if acq_item.is_dir():
                parser.print_usage()
                print("Error: Multiple AcqKnowledge directories given.")
                sys.exit(1)

    if args.write_markers:
        if args.marker_channel_index is None:
            parser.print_help()
            print("Error: Marker channel not specified.")
            sys.exit(1)
    
    if args.marker_map is not None:
        print("Error: Marker map file has not been implemented yet.")
        sys.exit(1)

    if isinstance(args.header_settings, Path):
        if not args.header_settings.exists():
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
            output_folder=args.output_folder,
            acq=acq_item,
            channel_indexes=args.channel_indexes,
            channel_names=args.channel_names,
            channel_scales=args.channel_scales,
            channel_units=args.channel_units,
            little_endian=args.little_endian,
            write_markers=args.write_markers,
            marker_channel_index=args.marker_channel_index,
            marker_map=args.marker_map,
            expected_nr_markers=args.expected_nr_markers,
            header_settings=args.header_settings,
        )

if __name__ == '__main__':
    main()