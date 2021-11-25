ACQ2BVA_DESCRIPTION = (
    "Write the data from an AcqKnowledge file to BrainVision Analyzer format."
)
ACQ2BVA_USAGE = """
    %(prog)s acq_file [acq_file ...] output_folder [optional args]
    %(prog)s acq_folder output_folder [optional args]

    If, and only if, the toml file specifies acq_file/folder and output_folder:
        %(prog)s [-s] toml_file [optional args]

    If, and only if, a toml file exists that specifies acq_file/folder and output_folder:
        %(prog)s

    %(prog)s [-h, --help]       Show this help message and exit
    %(prog)s -hh                Show the full help message with information on optional args and exit
    %(prog)s [-v, --version]    Show program's version number and exit

    %(prog)s [-p, --pc, --print_channels]
                                Print number and name of each channel, and exit


Path variables
  Either:
  -acq_file             File or files to convert from AcqKnowledge format to BrainVision Analyzer.
  -acq_folder           Folder containing files to convert from AcqKnowledge fromat to BrainVision Analyzer.
  
  output_folder         Folder where the raw data file, vhdr header file and, optionally, vmkr marker file
                        will be saved.
"""

ACQ2BVA_ARGUMENTS = """
Channel Variables:
  -c INDEX [INDEX ...], --ci INDEX [INDEX ...], --channel-indexes INDEX [INDEX ...]
    Description: Indexes of channels to include in raw file. Defaults to all channels.

  -n NAME [NAME ...], --names NAME [NAME ...], --channel-names NAME [NAME ...]
        Description: Names of the channels. Defaults to names given by AcqKnowledge. Useful for renaming channels to something more readable.

  --sc SCALE [SCALE ...], --scales SCALE [SCALE ...], --channel-scales SCALE [SCALE ...]
        Description: Scales for each channel. Defaults to 1 for every channel.

  -u UNIT [UNIT ...], --units UNIT [UNIT ...], --channel-units UNIT [UNIT ...]
        Description: Units for each channel. Defaults to units given by AcqKnowledge. Useful for fixing wrong units in recording.

Marker Variables:
  -m, --markers
        Description: Flag to write a marker file based on a specific marker channel. If true, then marker channel (--mc) must be specified. Optionally, marker map file (--mf) can be specified to provide a description of each marker value. Please refer to the ReadMe or Github page for explanation of a marker map file. Additionally, expected number of markers (--em) can be specified and a warning will be displayed if number of markers found does not correspond to that value.

  --mc INDEX, --marker-channel INDEX
        Description: A single channel index specifying which channel in the recording to scan for markers.

  --mf FILE, --marker-map-file FILE
        Description: Path of file specifying a marker mapping from the numerical value the description of that specific marker. For example, 1 -> 'Experiment start'. Please refer to the ReadMe or Github page for explanation of a marker map file.

  --em NR, --expected-nr-markers NR
        Description: Expected number of markers from each file. A warning will be displayed if number of markers found does not correspond with this value.

Header Toml Settings:
  --hs FILE, --header-settings FILE
        Description: Toml file to specify settings for the '.vhdr' file. Any setting written in here will override settings configured automatically by this program.

Acq2Bva Toml Settings:
  -s FILE, --settings FILE
        Description: Toml file to any and all settings specified above. Implicitly loaded if directory contains any of the following files: ["settings.toml", "acq2bva.toml", "acq.toml", "bva.tpml"]. Any setting written in here will be overwritten by settings in the command line. Header settings can be specified here under [header_settings].
"""