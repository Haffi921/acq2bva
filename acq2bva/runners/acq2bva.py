"""Write the data from an AcqKnowledge file channel to a text file.
Usage:
  acq2txt <acq_folder> <output_folder>
  acq2txt -h | --help
  acq2txt --version
Options:
  --version                         Show program's version number and exit.
  -h, --help                        Show this help message and exit.
  -i, --channel-indexes=<indexes>   The indexes of the channels to extract.
                                    Separate numbers with commas. Default is to
                                    extract all channels.
  -o, --outfile=<file>              Write to a file instead of standard out.
  --missing-as=<val>                What value to write where a channel is not
                                    sampled. [default: ]
The first column will always be time in seconds. Channel raw values are
converted with scale and offset into native units.
"""

from sys import argv

from docopt import docopt

from pathlib import Path

def main():
    args = argv[1:]
    pargs = docopt(
        __doc__,
        args,
        version="1.0.0"
    )
    acq_folder = Path(pargs["<acq_folder>"]).absolute()
    output_folder = Path(pargs["<output_folder>"]).absolute()
    if pargs['--channel-indexes']:
        channel_indexes = pargs['--channel-indexes']
    print(acq_folder)
    print(output_folder)
    print(channel_indexes)
    print(pargs)

if __name__ == '__main__':
    main()