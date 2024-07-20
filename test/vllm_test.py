
import shlex
import subprocess
from taskexp import Task, create_log_fd

# Intialized the test
exp = Task("python ./vllm/benchmarks/benchmark_throughput.py")
exp.fixed("--backend", "vllm")
exp.fixed("--model", "Llama-2-7b-chat-hf")
exp.arg("--num-prompts", [64, 128, 256])
exp.arg("--input-len", [128, 256, 512])
exp.arg("--output-len", [512, 1024])
exp.switch("--enable-mytool")

# Create log file
logfile = create_log_fd("throughtput_test", "./build/test_vllm")

# Execute the test
for task in exp.executable_loop():
    task.print_cmd()
    # task.execute(ostreams=[logfile])
    logfile.flush()
    task.update_tqdm()


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
                    output = subprocess.check_output(
                        shlex.split(cmd), universal_newlines=True)
                    logfile = create_log_fd(
                        "throughtput_test", "./build/test_vllm")
                    print(output, file=logfile, flush=True)
                except Exception as e:
                    pass
