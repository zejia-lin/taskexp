from datetime import datetime
import sys
import os
import subprocess
import shlex
import select
from enum import Enum
from typing import Any, Optional, Union, Callable, IO


def launch_subprocess(_cmd: Union[str, list[str]], timeout: float = 60,
                      ostreams: list[IO] = [sys.stdout], 
                      on_verbose: Callable[[str, IO, datetime], None] = None):
    
    def print_internal(line, all_io, all_str, all_stamp, callback, rio):
        now = datetime.now()
        all_io.append(rio)
        all_str.append(line)
        all_stamp.append(now)
        for stream in ostreams:
            stream.write(line)
        if callback:
            callback(line, rio, now)
    
    if isinstance(_cmd, str):
        cmd = shlex.split(_cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    all_strs, all_ios, all_stamps = [], [], []

    while True:
        selected = select.select([process.stdout, process.stderr], [], [])[0]
        for rio in selected:
            line = rio.readline()
            if not line:
                continue
            print_internal(line, all_ios, all_strs, all_stamps, on_verbose, rio)
        if process.poll() is not None:
            break

    # Process remaining output after the process has finished
    for line in process.stdout:
        print_internal(line, all_ios, all_strs, all_stamps, on_verbose, rio)    
    for line in process.stderr:
        print_internal(line, all_ios, all_strs, all_stamps, on_verbose, rio)

    process.stdout.close()
    process.stderr.close()
    process.wait()
    return all_strs, all_ios, all_stamps
    

class MultiRange:
    def __init__(self, ranges: list[int]):
        self.iterations = []
        for v in ranges:
            self.iterations.append(v)

    def __iter__(self):
        self.iter_index = 0
        self.total_iters = 1
        self.multi_index = [0] * len(self.iterations)
        for i in self.iterations:
            self.total_iters *= i
        return self

    def __next__(self):
        if self.iter_index < self.total_iters:
            temp = self.iter_index
            for i in range(len(self.iterations) - 1, -1, -1):
                self.multi_index[i] = temp % self.iterations[i]
                temp //= self.iterations[i]
            self.iter_index += 1
            return self.multi_index
        else:
            raise StopIteration()
        
    def status(self):
        return self.iter_index, self.multi_index


class Loopable:
    
    class FakeKey(Enum):
        FIXED = "__loopable_internal_fixed_nokey_argmt"
        POSIT = "__loopable_internal_positional_argmt"
        swich = "__loopable_internal_swich_argmt"
    
    def __init__(self):
        self.kv: dict[str, list] = {}
        self._nokey_argmt_count = {
            self.FakeKey.FIXED: 0,
            self.FakeKey.POSIT: 0,
            self.FakeKey.swich: 0
        }

    def fixed(self, key: Optional[str], value: str):
        if key is None:
            key = self._create_fake_key(self.FakeKey.FIXED)
        if not isinstance(value, str):
            raise TypeError(f"value {value} should be str")
        self.kv[key] = [value]
        return self

    def argmt(self, key: Optional[str], values: list[Any]):
        if key is None:
            key = self._create_fake_key(self.FakeKey.POSIT)
        if not isinstance(values, list):
            raise TypeError(f"values {values} should be list")
        self.kv[key] = [str(v) for v in values]
        return self
    
    def swich(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"value {value} should be str")
        key = self._create_fake_key(self.FakeKey.swich)
        return self.argmt(key, [value, ""])
    
    def index_loop(self):
        return MultiRange([len(x) for x in self.kv.values()])
    
    def execute(self):
        loop = self.index_loop()
        for kv_indices in loop:
            prompt_list = self._create_prompt_list(kv_indices)
            print(loop.status(), prompt_list)

    def _create_fake_key(self, keytype):
        key = f"{keytype}_{self._nokey_argmt_count[keytype]}"
        self._nokey_argmt_count[keytype] += 1
        return key
    
    def _create_raw_prompt_dict(self, kv_indices):
        result: dict[str, str] = {}
        for i, (key, vlist) in enumerate(self.kv.items()):
            result[key] = vlist[kv_indices[i]]
        return result
    
    def _create_prompt_list(self, kv_indices):
        prompt_dict = self._create_raw_prompt_dict(kv_indices)
        prompt_list = []
        for key, value in prompt_dict.items():
            if "FakeKey" in key:
                prompt_list.append(value)
            else:
                prompt_list.extend([key, value])
        return prompt_list


task = Loopable()
task.fixed("--backend", "vllm")
task.fixed(None, "f1")
task.fixed(None, "f2")
task.argmt("--requests", [16, 32, 64])
task.argmt("--tpcs", [54, 40, 30, 1])
task.argmt(None, ['a', 'b'])
task.argmt(None, ['x', 'y'])
task.swich("--enable-smctrl")
task.execute()

launch_subprocess("python ./runner_test.py")
