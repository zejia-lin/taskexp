from datetime import datetime
import sys
import os
import subprocess
import shlex
import select
from enum import Enum
from typing import Any, Optional, Callable

from task_runner import SubprocessLauncher


class MultiRange:
    def __init__(self, ranges: list[int], on_return: Callable[[int], Any]=None):
        self.iterations = []
        self.on_return = on_return
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
            if self.on_return is not None:
                return self.on_return(self.multi_index)
            return self.multi_index
        else:
            raise StopIteration()
    
    def total(self):
        return self.total_iters


class Loopable:
    
    class FakeKey(Enum):
        FIXED = "__loopable_internal_fixed_nokey_arg"
        POSIT = "__loopable_internal_positional_arg"
        SWITCH = "__loopable_internal_switch_arg"
    
    def __init__(self):
        self.kv: dict[str, list] = {}
        self._nokey_arg_count = {
            self.FakeKey.FIXED: 0,
            self.FakeKey.POSIT: 0,
            self.FakeKey.SWITCH: 0
        }

    def fixed(self, key: Optional[str], value: str):
        if key is None:
            key = self._create_fake_key(self.FakeKey.FIXED)
        if not isinstance(value, str):
            raise TypeError(f"value {value} should be str")
        self.kv[key] = [value]
        return self

    def arg(self, key: Optional[str], values: list[Any]):
        if key is None:
            key = self._create_fake_key(self.FakeKey.POSIT)
        if not isinstance(values, list):
            raise TypeError(f"values {values} should be list")
        self.kv[key] = [str(v) for v in values]
        return self
    
    def switch(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"value {value} should be str")
        key = self._create_fake_key(self.FakeKey.SWITCH)
        return self.arg(key, [value, ""])
    
    def index_loop(self):
        return MultiRange([len(x) for x in self.kv.values()])
    
    def cmd_loop(self):
        return MultiRange([len(x) for x in self.kv.values()], lambda idx: self.command_list(idx))
    
    def cmd_kv_loop(self):
        return MultiRange([len(x) for x in self.kv.values()], lambda idx: self.raw_command_dict(idx))
    
    def now(self, multi_index):
        curid = 0
        dims = [len(v) for v in self.kv.values()]
        acc_dim = 1
        for i in range(len(dims) - 1, -1, -1):
            curid += multi_index[i] * acc_dim
            acc_dim *= dims[i]
        return curid
    
    def execute(self):
        loop = self.index_loop()
        for kv_indices in loop:
            command_list = self.command_list(kv_indices)
            print(self.now(kv_indices), command_list)

    def _create_fake_key(self, keytype):
        key = f"{keytype}_{self._nokey_arg_count[keytype]}"
        self._nokey_arg_count[keytype] += 1
        return key
    
    def raw_command_dict(self, kv_indices):
        result: dict[str, str] = {}
        for i, (key, vlist) in enumerate(self.kv.items()):
            result[key] = vlist[kv_indices[i]]
        return result
    
    def command_list(self, kv_indices):
        command_dict = self.raw_command_dict(kv_indices)
        command_list = []
        for key, value in command_dict.items():
            if "FakeKey" in key:
                command_list.append(value)
            else:
                command_list.extend([key, value])
        return command_list


task = Loopable()
task.fixed("--backend", "vllm")
task.fixed(None, "f1")
task.fixed(None, "f2")
task.arg("--requests", [16, 32, 64])
task.arg("--tpcs", [54, 40, 30, 1])
task.arg(None, ['a', 'b'])
task.arg(None, ['x', 'y'])
task.switch("--enable-smctrl")
task.execute()

# for cmd in task.cmd_loop():
    # print(cmd)

launcher = SubprocessLauncher("python ./runner_test.py")
launcher.run()
