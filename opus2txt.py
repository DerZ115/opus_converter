import argparse
import os
import re

import numpy as np


def opus2txt(file):
    with open(file, "rb") as f:
        data = f.read()
    ramanDataRegex = re.compile(b"END\x00\x00\x00\x00\x00NPT")


opus2txt("files/EXTRACT.0")


# END.....NPT --> RAMAN?
