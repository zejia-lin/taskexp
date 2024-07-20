from datetime import datetime
import sys
import os
import shlex
from enum import Enum
from typing import Any, Optional, Callable, IO
from tqdm import tqdm
from copy import deepcopy

from task_runner import SubprocessRunner


def index_1d(now: list[int], dims: list[int]):
    curid = 0
    acc_dim = 1
    for i in range(len(dims) - 1, -1, -1):
        curid += now[i] * acc_dim
        acc_dim *= dims[i]
    return curid


def product(total: list[int]):
    tot = 1
    for dim in total:
        tot *= dim
    return tot
        


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


class TaskExecutable:
    def __init__(self, arg_list: list[str], env: dict[str, str] = None, arg_dict: dict[str, str] = None,
                 multi_index: list[int] = None, total_index: list[int] = None, pbar: tqdm = None):
        self.arg_list = arg_list
        self.env = env
        self.arg_dict = arg_dict
        self.multi_index = multi_index
        self.total_index = total_index
        self.pbar = pbar
        self.runner = None
        self.start_time = None
        self.end_time = None
    
    def execute(self, timeout: float = 300,  ostreams: list[IO] = [sys.stdout], 
                on_verbose: Callable[[str, IO, datetime], None] = None):
        self.runner = SubprocessRunner(cmd=self.arg_list, timeout=timeout, ostreams=ostreams,
                                      env=self.env, on_verbose=on_verbose)
        self.start_time, self.end_time = self.runner.run()
    
    def print_cmd(self, ostreams: list[IO] = [sys.stdout]):
        for fout in ostreams:
            print(' '.join(self.arg_list), file=fout)

    def update_tqdm(self):
        if self.pbar:
            self.pbar.update()
    
    def print_status(self, ostreams: list[IO] = [sys.stdout]):
        if self.multi_index and self.total_index:
            index = index_1d(self.multi_index, self.total_index)
            total = product(self.total_index)
            info = f"{index} / {total}, {self.multi_index} / {self.total_index}"
            for fout in ostreams:
                print(info, file=fout)
    
    def print_duration(self, ostreams: list[IO] = [sys.stdout]):
        for fout in ostreams:
            print(self.end_time - self.start_time, fout=fout)


class TaskIterator:
    def __init__(self, that, env: dict[str, str] = None):
        self.that = that
        self.env = env
    
    def __iter__(self):
        self.loop = iter(self.that.index_loop())
        self.pbar = tqdm(total=product(self.that.index_dims()), dynamic_ncols=True)
        return self

    def __next__(self):
        while idx := next(self.loop):
            cmd = task.arg_list(idx)
            cmd_dict = task.arg_dict(idx)
            return TaskExecutable(cmd, self.env, cmd_dict, idx, self.that.index_dims(), self.pbar)
        self.pbar.close()
        raise StopIteration()


class Experiement:
    
    class FakeKey(Enum):
        FIXED = "__loopable_internal_fixed_nokey_arg"
        POSIT = "__loopable_internal_positional_arg"
        SWITCH = "__loopable_internal_switch_arg"
    
    def __init__(self, program = None):
        self.kv: dict[str, list] = {}
        self.program = program and shlex.split(program)
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
        return MultiRange(self.index_dims())
    
    def cmd_loop(self):
        return MultiRange(self.index_dims(), lambda idx: self.arg_list(idx))
    
    def cmd_kv_loop(self):
        return MultiRange(self.index_dims(), lambda idx: self.arg_dict(idx))
    
    def executable_loop(self, env: dict[str, str] = None):
        return TaskIterator(self, env)
    
    def index_1d(self, multi_index):
        return index_1d(multi_index, self.index_dims())
    
    def index_dims(self):
        return [len(v) for v in self.kv.values()]
    
    def __len__(self):
        return product([len(v) for v in self.kv.values()])

    def _create_fake_key(self, keytype):
        key = f"{keytype}_{self._nokey_arg_count[keytype]}"
        self._nokey_arg_count[keytype] += 1
        return key
    
    def arg_dict(self, kv_indices):
        result: dict[str, str] = {}
        for i, (key, vlist) in enumerate(self.kv.items()):
            result[key] = vlist[kv_indices[i]]
        return result
    
    def arg_list(self, kv_indices):
        command_dict = self.arg_dict(kv_indices)
        if self.program is not None:
            command_list = deepcopy(self.program)
        else:
            command_list = []
        for key, value in command_dict.items():
            if "FakeKey" in key:
                command_list.append(value)
            else:
                command_list.extend([key, value])
        return command_list


class TaskLogger:
    def __init__(self, verbose = True, basedir: str = None, prefix: str = None, 
                 timefmt="%Y-%m-%d_%H:%M:%S", suffix: str = '.log'):
        self.verbose = verbose
        if basedir is not None:
            self.basedir = basedir
            self.prefix = prefix
            self.timefmt = timefmt
            self.suffix = suffix
            self.now = datetime.now()
            self.now_str = self.now.strftime(timefmt)
            self.filename = os.path.join(basedir, f"{prefix}{self.now_str}{suffix}")
            self.fd = open(self.filename, "w+")

    def write(self, msg: str, flush=False):
        if self.verbose:
            print(msg, end='', flush=flush)
        self.fd.write(msg)
    
    def close(self):
        if self.fd is not None:
            self.fd.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

            

task = Experiement("python ./runner_test.py")
task.fixed("--backend", "vllm")
task.fixed(None, "f1")
task.fixed(None, "f2")
task.arg("--requests", [16, 32, 64])
task.arg("--tpcs", [54, 40, 30, 1])
task.arg(None, ['a', 'b'])
task.arg(None, ['x', 'y'])
task.switch("--enable-smctrl")
# task.execute()
# print(task.total())

for idx in task.index_loop():
    print(task.index_1d(idx), task.arg_list(idx))
    # TaskExecutable(task.arg_list(idx)).execute()

for t in task.executable_loop():
    # print(t)
    # t.print_cmd()
    t.update_tqdm()
    t.execute()