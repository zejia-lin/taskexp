from datetime import datetime
import sys
import os
import subprocess
import shlex
import select
from typing import Union, Callable, IO, List
from functools import wraps

from safe_context import catch_all


class SubprocessRunner:
    def __init__(self, 
                 cmd: Union[str, List[str]], 
                 timeout: float = 300, 
                 ostreams: List[IO] = [sys.stdout],
                 env: dict[str, str] = None,
                 on_verbose: Callable[[str, IO, datetime], None] = None):
        self.cmd = cmd
        if isinstance(cmd, str):
            self.cmd = shlex.split(cmd)
        self.timeout = timeout
        self.ostreams = ostreams
        self.env = env
        self.on_verbose = on_verbose
        
        self.all_strs: List[str] = []
        self.all_ios: List[IO] = []
        self.all_stamps: List[datetime] = []

    @catch_all
    def _print_internal(self, line: str, rio: IO) -> None:
        now = datetime.now()
        self.all_ios.append(rio)
        self.all_strs.append(line)
        self.all_stamps.append(now)
        for stream in self.ostreams:
            stream.write(line)
        if self.on_verbose:
            self.on_verbose(line, rio, now)

    @catch_all
    def run(self):
        process = subprocess.Popen(self.cmd, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        start_time = datetime.now()
        last_output = datetime.now()
        while True:
            ready_reads, _, _ = select.select([process.stdout, process.stderr], [], [], self.timeout)
            if not ready_reads:
                if True or (datetime.now() - last_output).total_seconds() > self.timeout:
                    process.terminate()
                    process.wait()
                    return
            for rio in ready_reads:
                line = rio.readline()
                if not line:
                    continue
                self._print_internal(line, rio)
                last_output = datetime.now()
            if process.poll() is not None:
                break

        # Process remaining output after the process has finished
        for line in process.stdout:
            self._print_internal(line, process.stdout)    
        for line in process.stderr:
            self._print_internal(line, process.stderr)

        process.stdout.close()
        process.stderr.close()
        process.wait()
        end_time = datetime.now()
        return start_time, end_time