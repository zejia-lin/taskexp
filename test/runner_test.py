import time
from tqdm import tqdm
import signal
import sys
import os

print(os.environ["LD_LIBRARY_PATH"])

pbar = tqdm(total=80, dynamic_ncols=True)

for i in range(80):
    pbar.update(1)
    time.sleep(0.01)

task = Experiement("python ./runner_test.py")
task.fixed("--backend", "vllm")
task.fixed(None, "f1")
task.fixed(None, "f2")
task.arg("--requests", [16, 32, 64])
task.arg("--tpcs", [54, 40, 30, 1])
task.arg(None, ['a', 'b'])
task.arg(None, ['x', 'y'])
task.switch("--enable-smctrl")
logfile = create_log_fd("test_logger", "/home/lzj/work/llm-infer/AMotivation/taskify/build")

for t in task.executable_loop():
    t.execute(ostreams=[logfile])
    logfile.flush()
    t.update_tqdm()