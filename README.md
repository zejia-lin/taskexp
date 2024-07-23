# TaskExp

Run multiple loops of parameterized experiements. Capture all screen outputs, exceptions and keyboard interrupt.

```bash
git clone https://github.com/zejia-lin/taskexp.git
cd taskexp
pip install .
```

# Introduction

Traditionally, if we want to run experiements on a large set of combinational parameters, it is really tedious to code the `for` loops, capture outputs, write log files, and track experiement progress.
Sometimes may even accidentally press `Ctrl+C` during the process 😱.


```python
import subprocess
import shlex
for num_prompts in [64, 128, 256]:
    for input_len in [128, 256, 512]:
        for output_len in [512, 1024]:
            for enable_mytool in ["--enable-mytool", ""]:
                cmd = f"""python ./vllm/benchmarks/benchmark_throughput.py
                            --backend vllm
                            --model Llama-2-7b-chat-hf
                            --num-prompts {num_prompts}
                            --input-len {input_len}
                            --output-len {output_len}
                            {enable_mytool}
                """
                try:
                    output = subprocess.check_output(shlex.split(cmd), universal_newlines=True)
                    logfile = create_log_fd("throughtput_test", "./build/test_vllm")
                    print(output, file=logfile, flush=True)
                except Exception as e:
                    pass
```

# Usage

TaskExp is the solution for the above problems. Writing the equivalent code with TaskExp looks like:
```python
# Intialized the loops
from taskexp import Task, create_log_fd
exp = Task("python ./vllm/benchmarks/benchmark_throughput.py")
exp.fixed("--backend", "vllm")
exp.fixed("--model", "Llama-2-7b-chat-hf")
exp.arg("--num-prompts", [64, 128, 256])
exp.arg("--input-len", [128, 256, 512])
exp.arg("--output-len", [512, 1024])
exp.switch("--enable-mytool")

# Create log file
logfile = create_log_fd("throughtput_test", "./build/test_vllm")

# All the for loops creates 168 combinations of parameters
# Execute the all the tasks in a plain loop
for task in exp.executable_loop():
    task.print_cmd(ostreams=[logfile])
    task.execute(ostreams=[logfile])
    logfile.flush()
    task.update_tqdm()
```

There would be a live `tqdm` progress bar tracking the number of remaining loops. `stdout` and `stderr` from the executed tasks are write to the log file.
```bash
100%|██████████| 168/168 [2:27:26<00:00, 52.65s/it
```

You may also disable the progress bar and prints the task outputs on the screen.
```python
import sys
for task in exp.executable_loop(use_tqdm=False):
    task.print_cmd(ostreams=[sys.stdout, logfile])
    task.execute(ostreams=[sys.stdout, logfile])
    task.print_duration(ostreams=[sys.stdout, logfile])
```

## Exception and Interruption Handle

When encounter exceptions, the loop continues to the next task. On keyboard interrupt, it prompts a message ask if to exit.
```bash
Interrupt received. Do you want to exit? (yes/no):
```

# Features

## Loop Specification

The `Task` class is the container of the loops. Three types of arguments are supported.
- `Task.fixed(key, value)`: fixed argument that won't be contained in the loop
- `Task.arg(key, list_of_values)`: arguments in a loop
- `Task.switch(key)`: a keyword only argument, e.g. `Task.switch("-O3")` is equivalent to `for o3 in ["-O3", ""]:`

To pass positional argument rather than keyword argument, set the `key` parameter to None. 

## To be done...
