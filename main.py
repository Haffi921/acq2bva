from __future__ import annotations

from pathlib import Path

import bioread
from bioread.writers import matlabwriter

from error import true_or_exit, true_or_fail

acq_folder = Path("acq_data")
templates_path = Path("templates")
header_path, marker_path = (templates_path / "header_file.vhdr"), (templates_path / "marker_file.vmrk")
export_folder = Path("bva_data")

true_or_exit(acq_folder.exists() and acq_folder.is_dir(), "No 'acq_data' folder to work with")
true_or_exit(templates_path.exists() and acq_folder.is_dir(), "No templates to write for each file")
true_or_exit(header_path.exists() and header_path.is_file(), "No template header file (.vhdr) exists")

acq_files: list[Path] = []

for acq_file in acq_folder.iterdir():
    if acq_file.suffix == ".acq":
        acq_files.append(acq_file)

true_or_exit(len(acq_files), "No AcqKnowledge found in 'acq_data'")

export_folder.mkdir(exist_ok=True)

for acq_file in acq_files:
    export_header = export_folder / acq_file.with_suffix(".vhdr").name
    
    export_header.write_text(header_path.read_text())

acq_file = bioread.read(str(acq_files[0]))

