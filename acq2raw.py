import struct
def float2bin_ieee32bit():
    bin_rep = ""
    for c in struct.pack("f", 0.1):
        bin_rep += bin(c).replace("0b", "").rjust(8, "0")
    return bin_rep