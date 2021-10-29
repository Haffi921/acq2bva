from __future__ import annotations

from pathlib import Path

import bioread
from bioread.biopac import Channel

from acq2bva.util.error import true_or_fail


class VHDRInfos:
    """
    Very basic Toml writer for BVA's vhdr files specification
    """

    def __init__(self, infos_settings: dict = {}) -> None:
        self.set_settings(infos_settings)

    def set_settings(self, infos_settings: dict):
        for key, value in infos_settings.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_name(self) -> str:
        return "[Comment]"

    def generate_text(self) -> str:
        return_string = f"{self.get_name()}"

        for key, val in vars(self).items():
            if val is not None:
                return_string += f"\n{key}={val}"

        return return_string


class CommonInfos(VHDRInfos):
    def __init__(
        self,
        data_file: str,  # Paths
        channels: list[Channel],  # Channels
        samples_per_second: float = 2000.0,  # Raw data
        marker_file: str = None,  # Markers
        common_infos: dict = {},  # Other settings
    ) -> None:

        # Common Infos settings
        self.DataFile = data_file
        self.MarkerFile = marker_file
        self.DataFormat = "BINARY"
        self.DataOrientation = "VECTORIZED"
        self.DataType = "TIMEDOMAIN"
        self.NumberOfChannels = len(channels)
        self.SamplingInterval = int(1_000_000 // samples_per_second)

        super().__init__(common_infos)

    def get_name(self) -> str:
        return "[Common Infos]"


class BinaryInfos(VHDRInfos):
    def __init__(
        self,
        little_endian: bool = True,  # Raw data
        binary_infos: dict = {},  # Other settings
    ) -> None:
        # Binary Infos settings
        self.BinaryFormat = "IEEE_FLOAT_32"
        self.UseBigEndianOrder = "NO" if little_endian else "YES"

        super().__init__(binary_infos)

    def get_name(self) -> str:
        return "[Binary Infos]"


class ChannelInfos(VHDRInfos):
    def __init__(
        self,
        channels: list[Channel],  # All channels
        names: list = None,
        scales: list = None,
        units: list = None,
    ) -> None:
        if names is None:
            names = [channel.name for channel in channels]
        if scales is None:
            scales = [1] * len(channels)
        if units is None:
            units = [channel.units for channel in channels]

        true_or_fail(
            len(names) == len(scales) == len(units) == len(channels),
            "Names, scales and units specified must equal the number of channels being processed",
        )

        for i in range(len(channels)):
            channel_var = f"Ch{i + 1}"
            setattr(self, channel_var, f"{names[i]},,{scales[i]},{units[i]}")

    def get_name(self) -> str:
        return "[Channel Infos]"


class HeaderInfos:
    def __init__(
        self,
        # Path
        data_file: str,
        # Channels
        channels: list[Channel],
        ch_names: list = None,
        ch_scales: list = None,
        ch_units: list = None,
        # Raw data
        samples_per_second: float = 2000.0,
        little_endian: bool = True,
        # Markers
        marker_file: str = None,
        # Other settings
        header_settings: dict = {},
    ) -> None:

        # Header file components
        self.common_infos = CommonInfos(
            data_file=data_file,  # Paths
            channels=channels,  # Channels
            samples_per_second=samples_per_second,  # Raw data
            marker_file=marker_file,  # Markers
            common_infos=header_settings,  # Other settings
        )
        self.binary_infos = BinaryInfos(
            little_endian=little_endian,  # Raw data
            binary_infos=header_settings,  # Other settings
        )
        self.channel_infos = ChannelInfos(
            channels=channels,  # All channels
            names=ch_names,
            scales=ch_scales,
            units=ch_units,
        )

    def generate_text(self):
        return_string = "Brain Vision Data Exchange Header File Version 1.0"

        return_string += f"\n\n{self.common_infos.generate_text()}"
        return_string += f"\n\n{self.binary_infos.generate_text()}"
        return_string += f"\n\n{self.channel_infos.generate_text()}"

        return return_string


def acq2vhdr(
    # Paths
    output_file: Path,
    data_file: str,
    # Channels
    channels: list[Channel],
    ch_names: list = None,
    ch_scales: list = None,
    ch_units: list = None,
    channel_indexes: list[int] = None,
    # Raw data
    samples_per_second: float = 2000.0,
    little_endian: bool = True,
    # Markers
    marker_file: str = None,
    # Other settings
    header_settings: dict = {},
):
    """
    Writes a '.vhdr' file for BrainVision Analyzer
    """

    # Select channels
    if channel_indexes is not None:
        channels = [channels[i] for i in channel_indexes]

    # Create infos
    header_infos = HeaderInfos(
        # Paths
        data_file,
        # Channels
        channels,
        ch_names,
        ch_scales,
        ch_units,
        # Raw data
        samples_per_second,
        little_endian,
        # Markers
        marker_file,
        # Other settings
        header_settings,
    )

    # Write file
    with output_file.open("wt") as header:
        header.write(header_infos.generate_text())


if __name__ == "__main__":
    data_file = Path("Feedback03.dat")
    marker_file = data_file.with_suffix(".vmrk")
    acq = bioread.read(str(Path("acq_data/Feedback03.acq")))

    header = HeaderInfos(
        data_file.name,
        acq.channels,
        marker_file.name,
        ch_names=[
            "EMG",
            "Bit1",
            "Bit2",
            "Bit3",
            "Bit4",
            "Bit5",
            "Bit6",
            "Bit7",
            "Marker",
        ],
        ch_units=["mV", "Bits", "Bits", "Bits", "Bits", "Bits", "Bits", "Bits", "Bits"],
        samples_per_second=acq.samples_per_second,
        little_endian=True,
    )

    print(header.generate_text())
