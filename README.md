# TaskExp

TaskExp is a driver to run multiple loops of experiements with hyperparameters. It captures all screen outputs, exceptions and keyboard interrupt.


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

# Quick Start

## Simple Usage

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

## Tracking Output

There would be a live `tqdm` progress bar tracking the number of remaining loops. `stdout` and `stderr` from the executed tasks are write to the log file.
```bash
100%|██████████| 168/168 [2:27:26<00:00, 52.65s/it
```

The progress bar can also be dsiabled and prints the task outputs on the screen.
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

# Detailed Usage

## Loop Specification

Initialize a task object.

```python
from taskexp import Task
task = Task("gcc")
```


The `Task` class is the container of the loops. Three types of arguments are supported.

1. Fixed argument that won't be contained in the loop, e.g. the input files.
```python
task.fixed("key", "value")
```

2. Arguments that are looped in the experiement, e.g. the hyper parameters, configurations.
```python
task.arg("key", [1024, 2048, 4096, 8192, 16384])
```

3. Keyword only argument, e.g. enabling `-O3` or not.
```python
task.switch("-O3")
# this is a wrapper equivalent to
task.arg(None, ["-O3", ""])
```

4. To pass positional argument rather than keyword argument, set the `key` parameter to `None` in the above example.


## Start the experiement

After configured the loop, the `Task` flattens all the nested `for` loops in one plain loop in the order the loops are configured. 

```python
for exe in task.executable_loop():
    exe.execute(ostreams=[sys.stdout])
```

The `stdout/stderr` from executable are redirected to `ostreams`, a list of objects that has the `write` methods. Therefore it can also write to a log file.

```python
with open("myexp.log", "w+") as fout:
    for exe in task.executable_loop():
        exe.execute(ostreams=[sys.stdout, fout])
        fout.flush()
```

The `executable_loop` can be started at arbitrary index if the previous experiement is interrupted.

```python
for exe in task.executable_loop(start=10):
```

By default, there is a `tqdm` progress bar and can be disabled.

```python
for exe in task.executable_loop(use_tqdm=False):
```

## Customizing the Execution

The `executable_loop` returns a `TaskExecutable` object by each iteration. It has several methods to monitor the task, all of which has a `ostreams` argument to redirect the output.
- `execute`: execute the task using Python `subprocess`
- `print_cmd`: prints the command line to run this task
- `update_tqdm`: updates the `tqdm` bar
- `print_status`: print the current index of the flattened loop
- `print_duration`: print the elapsed time of this task

The most important method is the `execute`, its signature is:
```python
def execute(self, timeout: float = 300,  ostreams: list[IO] = [sys.stdout], 
                on_verbose: Callable[[str, IO, datetime], None] = None)
```
- `timeout`: kill the subprocess after timeout
- `ostreams`: redirect the output from subprocess
- `on_verbose`: callback on the subprocess prints a line