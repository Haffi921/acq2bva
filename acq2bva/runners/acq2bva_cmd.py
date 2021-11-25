# """Write the data from an AcqKnowledge file to BrainVision Analyzer format.
# """
from __future__ import annotations

import sys
from pathlib import Path
import bioread

import tomli as toml

from acq2bva.writers.acq2bva import acq2bva
from acq2bva.runners.acq2bva_args import create_parser
from acq2bva.runners.acq2bva_text import ACQ2BVA_DESCRIPTION, ACQ2BVA_ARGUMENTS

TOML_POSSIBILITES = ["settings.toml", "acq2bva.toml", "acq.toml", "bva.tpml"]

def main():
    parser = create_parser()
    args = parser.parse_args()

    # -------------------------------------
    # Functions
    # -------------------------------------
    def fatal_exit(msg):
        parser.print_usage()
        print(msg)
        sys.exit(1)

    def print_help():
        print(ACQ2BVA_DESCRIPTION, end="\n\n")
        parser.print_usage()
        if args.help > 1:
            print(ACQ2BVA_ARGUMENTS)
        sys.exit(0)

    def print_channels(acq: list[Path]):
        def get_acq_files(acq_item: Path, acq_files: list = []) -> list:
            if acq_item.is_dir():
                for acq_file in acq_item.iterdir():
                    get_acq_files(acq_file, acq_files)
            elif acq_item.is_file() and acq_item.suffix == ".acq":
                acq_files.append(acq_item)
            return acq_files
        
        acq_files = [
            acq_file
            for acq_item in acq
            for acq_file in get_acq_files(acq_item)
        ]
        
        for acq_file in acq_files:
            print(f"{acq_file}:")
            acq_data = bioread.read(str(acq_file))
            for i, channel in enumerate(acq_data.channels):
                print(f"{i}: {channel.name}")
        sys.exit(0)
        
    def load_settings():
        settings = {}

        for toml_file in [args.settings, *TOML_POSSIBILITES]:
            if toml_file is not None and Path(toml_file).is_file():
                with Path(toml_file).open() as f:
                    settings = {
                        "write_markers": False,
                        **toml.load(f)
                    }
                break
        
        for key, val in vars(args).items():
            if key not in settings or val is not None:
                settings[key] = val

        return settings
            
    def determine_input_and_output(settings):
        acq = None
        output_folder = None

        acq_file = settings.get("acq_file")
        acq_folder = settings.get("acq_folder")
        output_folder = settings.get("output_folder")

        if output_folder and isinstance(output_folder, str):
            output_folder = Path(output_folder)
            if acq_file:
                if isinstance(acq_file, list):
                    acq = [Path(acq_item) for acq_item in acq_file]
                elif isinstance(acq_file, str):
                    acq = [Path(acq_file)]
            elif acq_folder and isinstance(acq_folder, str):
                acq = [Path(acq_folder)]

        if len(args.rest) > 0:
            if len(args.rest) > 1:
                output_folder: Path = Path(args.rest.pop())
            acq: list[Path] = list(map(Path, args.rest))

        if acq is None:
            fatal_exit("\nError: Missing acq_file or acq_folder")
        if output_folder is None:
            fatal_exit("\nError: Missing output_folder")

        if len(acq) > 1:
            for acq_item in acq:
                if acq_item.is_dir():
                    fatal_exit("\nError: Multiple AcqKnowledge directories given.")
        
        return acq, output_folder
    
    def validate_settings(settings):
        # Channel settings should be a list of ints
        if isinstance(settings["channel_indexes"], int):
            settings["channel_indexes"] = [settings["channel_indexes"]]

        # Marker channel must be indicated if write_markers is true
        if settings["write_markers"]:
            if settings["marker_channel_index"] is None:
                fatal_exit("\nError: Marker channel not specified.")

        # If marker map is a path, check if exists and then load it as dictionary
        if isinstance(settings["marker_map"], Path):
            if not settings["marker_map"].exists():
                fatal_exit("\nError: Marker map file does not exist.")

            with settings["marker_map"].open() as f:
                settings["marker_map"] = toml.load(f)

        # If header settings is a path, check if exists and then load it as dictionary
        if isinstance(settings["header_settings"], Path):
            if not settings["header_settings"].exists():
                fatal_exit("\nError: Header settings file does not exist.")

            with settings["header_settings"].open() as f:
                settings["header_settings"] = toml.load(f)
    
    def parse_marker_map(marker_map: dict):
        new_map = {}
        for marker, desc in marker_map.items():
            try:
                start, end = marker.split("-")
                new_map[range(int(start), int(end) + 1)] = desc
            except:
                new_map[int(marker)] = desc
        return new_map

    # -------------------------------------

    if args.help:
        print_help()

    settings = load_settings()

    acq, output_folder = determine_input_and_output(settings)

    if args.print_channels:
        print_channels(acq)

    validate_settings(settings)

    if isinstance(settings["marker_map"], dict):
        settings["marker_map"] = parse_marker_map(settings["marker_map"])

    for acq_item in acq:
        if not acq_item.exists():
            fatal_exit(f"\nError: {acq_item} is does not exist")

        acq2bva(
            # Paths
            output_folder=output_folder,
            acq=acq_item,

            # Channels
            channel_indexes=settings["channel_indexes"],
            channel_names=settings["channel_names"],
            channel_scales=settings["channel_scales"],
            channel_units=settings["channel_units"],

            # Markers
            write_markers=settings["write_markers"],
            marker_channel_index=settings["marker_channel_index"],
            marker_map=settings["marker_map"],
            expected_nr_markers=settings["expected_nr_markers"],

            # Other
            header_settings=settings["header_settings"],
        )


if __name__ == "__main__":
    main()
