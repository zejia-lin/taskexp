import sys
from taskexp import Task, create_log_fd

task = Task("python ./runner_test_proc.py")
task.fixed("--backend", "vllm")
task.fixed(None, "f1")
task.fixed(None, "f2")
task.arg("--requests", [16, 32, 64])
task.arg("--tpcs", [54, 40, 30, 1])
task.arg(None, ['a', 'b'])
task.arg(None, ['x', 'y'])
task.switch("--enable-smctrl")
logfile = create_log_fd("test_logger", "/home/lzj/work/llm-infer/AMotivation/taskexp/build")


for t in task.executable_loop():
    t.execute(ostreams=[logfile])
    # logfile.flush()
    t.update_tqdm()