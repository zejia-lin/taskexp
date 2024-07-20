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

This is roughly equivalent to the following tedious code. However, the code below not yet has functionalities for the logging, progress checking, capturing live output, and other misc stuffs.
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


## Exception and Interruption

All exceptions are caught. To interrupt, type `Ctrl+C`, and `yes`.
