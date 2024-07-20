import time
from tqdm import tqdm
import signal
import sys
import os

# print(os.environ["LD_LIBRARY_PATH"])

pbar = tqdm(total=80, dynamic_ncols=True)

for i in range(80):
    pbar.update(1)
    time.sleep(0.01)

