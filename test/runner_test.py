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
task.switch("--enable")
logfile = create_log_fd("test_logger", "../build")


for t in task.executable_loop(False):
    # pass
    t.execute(ostreams=[logfile])
    # t.print_cmd(ostreams=[logfile])
    # t.print_duration(ostreams=[logfile])
    # t.print_status(ostreams=[logfile])
    # logfile.flush()
    # t.update_tqdm()