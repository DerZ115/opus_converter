import argparse
import os
import re
import struct

import numpy as np


def opus2txt(file, meta=False):
    """Extract data from a binary OPUS file.

    Args:
        file (str): Path to OPUS file.
        meta (bool, optional): !TBA! Whether metadata of the file should be returned. Defaults to False.

    Returns:
        array: Spectral data from the file, with wavenumbers in the first and intensities in the second column.
    """
    with open(file, "rb") as f:
        data = f.read()

    ramanDataRegex = re.compile(
        b"END\x00{5}NPT\x00{3}\x02\x00(.{4})"
        b"FXV\x00\x01\x00\x04\x00(.{8})"
        b"LXV\x00\x01\x00\x04\x00(.{8})"
        b"CSF\x00.{12}MXY\x00.{12}MNY\x00.{12}"
        b"DPF\x00.{8}DAT\x00.{4}(.{10})\x00\x00"
        b"TIM\x00.{4}(.{16}).{4}DXU\x00.{8}"
        b"END\x00.{8}(.*?)\x00{4}NPT", 
        flags=re.DOTALL)
    
    mo = ramanDataRegex.search(data)
    npt, fxv, lxv, dat, tim, ints = mo.groups()

    npt = struct.unpack("<I", npt)[0]
    fxv = struct.unpack("<d", fxv)[0]
    lxv = struct.unpack("<d", lxv)[0]
    dat = dat.decode("ascii")
    tim = tim.decode("ascii")

    wns = np.linspace(fxv, lxv, npt)
    ints = np.asarray(struct.unpack("<" + "f"*npt, ints))

    data_out = np.column_stack((wns,ints))

    return data_out

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert binary OPUS files to csv-style text files."
        )
    
    file_import = parser.add_mutually_exclusive_group(required=True)
    file_import.add_argument("-f", "--file", metavar="path", type=str, nargs="+", action="store", help="File or files to be converted.")
    file_import.add_argument("-d", "--dir", metavar="path", type=str, nargs=1, action="store", help="Directory containing the files to be converted")
    parser.add_argument("-o", "--out",metavar="path", type=str, nargs=1, action = "store", help="Output directory for converted files", required=True)

    args = parser.parse_args()
    
    if args.dir:
        files = os.listdir(args.dir[0])
        dir = args.dir[0]
    else:
        files = args.file
        dir = ""
    
    dir_out = args.out[0]

    if not os.path.isdir(dir_out):
        os.mkdir(dir_out)
    
    for i, file in enumerate(files):
        print(f"File {i+1}/{len(files)}.")

        filepath = os.path.join(dir, file)
        outpath = os.path.join(dir_out, file.split("/")[-1] + ".csv")

        data = opus2txt(filepath)

        np.savetxt(outpath, data, delimiter=",", fmt="%.6f")
    
    print("Done.")