import time
from tqdm import tqdm
import signal
import sys
import os

# print(os.environ["LD_LIBRARY_PATH"])

pbar = tqdm(total=20, dynamic_ncols=True)

for i in range(20):
    pbar.update(1)
    time.sleep(0.01)

