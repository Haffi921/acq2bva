import argparse

from pathlib import Path

from acq2bva.__version__ import __version__
from acq2bva.runners.acq2bva_text import ACQ2BVA_USAGE

def create_parser():
    parser = argparse.ArgumentParser(
        prog="acq2bva", usage=ACQ2BVA_USAGE, add_help=False
    )
    parser.add_argument("-h", "--help", action="count", default=0)
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s version " + __version__
    )
    parser.add_argument("-p", "--pc", "--print-channels", action="store_true", dest="print_channels")
    parser.add_argument("rest", nargs=argparse.REMAINDER)

    # Channels
    parser.add_argument(
        "-c",
        "--ci",
        "--channel-indexes",
        nargs="+",
        type=int,
        dest="channel_indexes",
    )
    parser.add_argument(
        "-n",
        "--names",
        "--channel-names",
        nargs="+",
        type=str,
        dest="channel_names",
    )
    parser.add_argument(
        "--sc",
        "--scales",
        "--channel-scales",
        nargs="+",
        type=str,
        dest="channel_scales",
    )
    parser.add_argument(
        "-u",
        "--units",
        "--channel-units",
        nargs="+",
        type=str,
        dest="channel_units",
    )

    # Raw data
    parser.add_argument(
        "--be",
        "--big-endian",
        type=bool,
        dest="little_endian",
    )

    # Markers
    parser.add_argument(
        "-m",
        "--markers",
        type=bool,
        dest="write_markers",
    )
    parser.add_argument(
        "--mc",
        "--marker-channel",
        action="store",
        type=int,
        dest="marker_channel_index",
    )
    parser.add_argument(
        "--mf",
        "--marker-map-file",
        action="store",
        type=Path,
        dest="marker_map",
    )
    parser.add_argument(
        "--em",
        "--expected-nr-markers",
        action="store",
        type=int,
    )

    # Other settings
    parser.add_argument(
        "--hs",
        "--header-settings",
        action="store",
        type=Path,
        dest="header_settings",
    )

    # Other settings
    parser.add_argument(
        "-s",
        "--settings",
        action="store",
        type=Path,
        dest="settings",
    )

    return parser