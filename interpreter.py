#!/usr/bin/env python

from __future__ import print_function

import sys

from assemble_low import assemble


class VirtualMemoryError(IndexError):
    def __init__(self, addr):
        self.addr = addr


class Memory(object):
    def __init__(self, mem):
        self.mem = mem
        self.capacity = len(mem)

    @classmethod
    def blank(klass, capacity=1000):
        return klass([0] * capacity)

    def get(self, index, intermediate=False):
        if index == -1:
            if intermediate:
                return 0
            else:
                ch = sys.stdin.read(1)
                return ch

        if index < 0 or index >= self.capacity:
            raise VirtualMemoryError(index)
        return self.mem[index]

    def __getitem__(self, index):
        return self.get(index)

    def __setitem__(self, index, value):
        if index == -1:
            sys.stdout.write(chr(-value))
            return

        if index < 0 or index >= self.capacity:
            raise VirtualMemoryError(index)

        self.mem[index] = value

    def __repr__(self):
        return "Memory(%r)" % (self.mem,)


def run_vm(memory, start_addr=0, trace=False,
           max_instructions=float('inf')):
    i = start_addr
    insn_count = 0
    while True:
        # A negative address means 'exit'
        if i < 0:
            print("[vm] Exiting since IP < 0 (%d)" % (i,),
                  file=sys.stderr)
            break
        if insn_count > max_instructions:
            print("[vm] Exiting since instruction count > %d (%d)" % (max_instructions, i),
                  file=sys.stderr)
            break

        # Decode
        a = memory[i]
        b = memory[i + 1]
        c = memory[i + 2]

        if trace:
            print("[vm] %d: %d %d %d" % (i, a, b, c), file=sys.stderr)

        # Subtract
        existing = memory.get(b, intermediate=True)
        new = existing - memory[a]
        memory[b] = new

        if trace:
            print("[vm]     %d --> %d" % (existing, new), file=sys.stderr)

        # Branch
        if new <= 0:
            i = c
        else:
            i = i + 3

        insn_count += 1

    print("[vm] Ran %d instructions" % (insn_count,), file=sys.stderr)


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'rb') as f:
            raw_code = f.read()
    else:
        raw_code = sys.stdin.read()

    lines = raw_code.split('\n')

    start = int(lines[0].strip())
    code = [int(x) for x in lines[1].split(' ')]

    print('[vm] start = %d' % (start,), file=sys.stderr)
    vm = Memory(code)

    try:
        run_vm(vm, start_addr=start, trace=True, max_instructions=100)
    except VirtualMemoryError as e:
        print("VM accessed invalid memory: %d" % (e.addr,), file=sys.stderr)

    print(vm, file=sys.stderr)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
