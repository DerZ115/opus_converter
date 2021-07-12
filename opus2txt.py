import struct
import argparse
import numpy as np
import os

def parse_arguments():
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

    return files, dir, args.out[0]

files, dir, out_dir = parse_arguments()

# Create output directory if it doesn't exist
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)

for i, file in enumerate(files):

    print(f"File {i+1}/{len(files)}.") # Progress counter

    filepath = os.path.join(dir, file)
    outpath = os.path.join(out_dir, file + ".txt")

    with open(filepath, "rb") as f:
        data = f.read()
    
    data = data.split(sep=b'END\x00') # Split into data segments
    for i, segment in enumerate(data):
        if segment[-4:] == b'OK\x00\x00' and data[i+1][-4:] == b'WN\x00\x00': # Find segment containing Raman data (Wavenumbers and Intensities)
            wn_data = data[i+1]
            int_data = data[i+2]
            break

    wn_data = [wn_data[j:j+4] for j in range(0, len(wn_data), 4)] # Split into 4 Byte junks
    
    for j in range(len(wn_data)):
        if wn_data[j] == b'NPT\x00': # Number of data points
            npt = struct.unpack("<I", wn_data[j+2])[0] # Unsigned Integer, little Endian
        if wn_data[j] == b'FXV\x00': # First Wavenumber
            fxv = struct.unpack("<d", b''.join(wn_data[j+2:j+4]))[0] # Double float, Little Endian
        if wn_data[j] == b'LXV\x00': # Last Wavenumber
            lxv = struct.unpack("<d", b''.join(wn_data[j+2:j+4]))[0] # Double float, Little Endian

    # print(f"{npt}, {fxv}, {lxv}")

    wns = np.linspace(fxv, lxv, npt) # Create Wavenumber array

    int_data = int_data[8:8+npt*4] # Remove leading zeros and split into 4 Byte junks
    int_data = [int_data[j:j+4] for j in range(0, len(int_data), 4)]

    ints = np.zeros(npt) # Prepare empty array for Intensity data
    for j, val in enumerate(int_data):
        ints[j] = struct.unpack("<f", val)[0] # Float, Little Endian
    
    data_out = np.vstack((wns, ints)).T # Combine into one array

    np.savetxt(outpath, data_out, delimiter=",", fmt="%.6f")
    
print("Done.")