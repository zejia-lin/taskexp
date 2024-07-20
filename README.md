# TaskExp

Run multiple loops of parameterized experiements. Bypass exceptions and keyboard interrupt.


## Workflow
Intialized the test
```python
from taskexp import Task, create_log_fd
exp = Task("python ./vllm/benchmarks/benchmark_throughput.py")
exp.fixed("--backend", "vllm")
exp.fixed("--model", "Llama-2-7b-chat-hf")
exp.arg("--num-prompts", [64, 128, 256])
exp.arg("--input-len", [128, 256, 512])
exp.arg("--output-len", [512, 1024])
exp.switch("--enable-mytool")
```

Create log file
```python
logfile = create_log_fd("throughtput_test", "./build/test_vllm")
```

Execute the test. This writes program output to the log file, and update the test progress on `stdout`.
```python
for task in exp.executable_loop():
    task.execute(ostreams=[logfile])
    task.print_cmd(ostreams=[logfile])
    logfile.flush()
    task.update_tqdm()
```

## Exception and Interruption

All exceptions are caught. To interrupt, type `Ctrl+C`, and `yes`.
