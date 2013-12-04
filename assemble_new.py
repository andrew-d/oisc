#!/usr/bin/env python

from __future__ import print_function

import re
import sys
from numbers import Number


label_count = 0
def temp_label():
    global label_count
    label_count += 1
    return "__tmp_%d" % (label_count,)


# --------------------------------------------------

class Instruction(object):
    def __init__(self, A, B, C=None, label=None):
        self.A = A
        self.B = B
        self.C = C
        self.label = label
        self.address = None

    @property
    def size(self):
        return 3

    @property
    def is_instruction(self):
        return True

    @property
    def code(self):
        return [self.A, self.B, self.C]

    def __repr__(self):
        return "Instruction(%r, %r, %r)" % (self.A, self.B, self.C)


class DataInstruction(object):
    def __init__(self, data, label=None):
        if isinstance(data, int):
            self.data = [data]
        else:
            self.data = [self._conv(x) for x in data]
        self.label = label
        self.address = None

    def _conv(self, x):
        if isinstance(x, str):
            return ord(x[0])
        elif isinstance(x, Number):
            return int(x)
        else:
            raise ValueError(x)

    @property
    def size(self):
        return len(self.data)

    @property
    def is_instruction(self):
        return False

    @property
    def code(self):
        return list(self.data)

    def __repr__(self):
        return "DataInstruction(%r)" % (self.data,)


class CommentInstruction(object):
    def __init__(self, comment):
        self.comment = comment
        self.label = None

    def __repr__(self):
        return "CommentInstruction(%r)" % (self.comment,)

    @property
    def size(self):
        return 0

    @property
    def is_instruction(self):
        return False

    @property
    def code(self):
        return []


# --------------------------------------------------


class Node(object):
    """Abstract class"""
    MNEMONIC = ''
    NUM_OPS = 0

    def __init__(self, op1=None, op2=None, op3=None, label=None):
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3
        self.label = label

    def emit(self):
        insns = self._emit()

        # Apply the label (if any) to the first instruction.
        if self.label is not None and len(insns) > 0:
            insns[0].label = self.label

        return insns

    def _emit(self):
        raise NotImplementedError

    @property
    def as_string(self):
        s = self.MNEMONIC
        if self.NUM_OPS > 0:
            s += ' ' + str(self.op1)
        if self.NUM_OPS > 1:
            s += ', ' + str(self.op2)
        if self.NUM_OPS > 2:
            s += ', ' + str(self.op3)
        return s

    def __repr__(self):
        return "'" + self.as_string + "'"


class DataNode(Node):
    def _emit(self):
        return [
            DataInstruction(self.op1)
        ]

    @property
    def as_string(self):
        return None

    def __repr__(self):
        return "DataNode(%r)" % (self.op1,)


class SubleqNode(Node):
    MNEMONIC = 'subleq'
    NUM_OPS = 3

    def _emit(self):
        return [Instruction(self.op1, self.op2, self.op3)]


class MoveNode(Node):
    MNEMONIC = 'mov'
    NUM_OPS = 2

    def _emit(self):
        return [
            Instruction(self.op2, self.op2),
            Instruction(self.op1, 'Z'),
            Instruction('Z', self.op2),
            Instruction('Z', 'Z'),
        ]


class ZeroNode(Node):
    MNEMONIC = 'zero'
    NUM_OPS = 1

    def _emit(self):
        return [
            Instruction(self.op1, self.op1)
        ]


class AddNode(Node):
    MNEMONIC = 'add'
    NUM_OPS = 2

    def _emit(self):
        return [
            Instruction(self.op1, 'Z'),
            Instruction('Z', self.op2),
            Instruction('Z', 'Z'),
        ]


class AddImmNode(Node):
    MNEMONIC = 'addi'
    NUM_OPS = 2

    def _emit(self):
        imm_label = temp_label()
        ret = [
            Instruction('Z', 'Z', '$+4'),
            DataInstruction(self.op1, label=imm_label),
        ]

        ret.extend(AddNode(imm_label, self.op2).emit())
        return ret


class SubNode(Node):
    MNEMONIC = 'sub'
    NUM_OPS = 2

    def _emit(self):
        return [
            Instruction(self.op1, self.op2),
        ]


class SubImmNode(Node):
    MNEMONIC = 'subi'
    NUM_OPS = 2

    def _emit(self):
        imm_label = temp_label()
        ret = [
            Instruction('Z', 'Z', '$+4'),
            DataInstruction(self.op1, label=imm_label),
        ]

        ret.extend(SubNode(imm_label, self.op2).emit())
        return ret


class NopNode(Node):
    MNEMONIC = 'nop'
    NUM_OPS = 0

    def _emit(self):
        return [Instruction('Z', 'Z')]


class JumpNode(Node):
    MNEMONIC = 'jmp'
    NUM_OPS = 1

    def _emit(self):
        return [Instruction('Z', 'Z', self.op1)]


class JzNode(Node):
    MNEMONIC = 'jz'
    NUM_OPS = 2

    def _emit(self):
        return [
            Instruction(self.op1, 'Z', '$+6'),
            Instruction('Z', 'Z', '$+9'),
            Instruction('Z', 'Z'),
            Instruction('Z', self.op1, self.op2),
        ]


class BitshiftLeftNode(Node):
    MNEMONIC = 'shl'
    NUM_OPS = 2

    def _emit(self):
        # Rough idea:
        #           jmp $+5
        #   ctr:    db 0
        #   diff:   db 1
        #           mov src, ctr
        #   loop:   add dest, dest
        #           sub ctr, diff
        #           jz ctr, end
        #           jmp loop
        #   end:
        #

        ctr_lbl = temp_label()
        diff_lbl = temp_label()
        ret = [
            Instruction('Z', 'Z', '$+5'),
            DataInstruction(0, label=ctr_lbl),
            DataInstruction(1, label=diff_lbl),
        ]

        ret.extend(MoveNode(self.op2, ctr_lbl).emit())

        loop_lbl = temp_label()
        end_lbl = temp_label()

        ret.extend(AddNode(self.op1, self.op1, label=loop_lbl).emit())
        ret.extend(SubNode(diff_lbl, ctr_lbl).emit())
        ret.extend(JzNode(ctr_lbl, end_lbl).emit())
        ret.extend(JumpNode(loop_lbl).emit())
        ret.extend(NopNode(label=end_lbl).emit())

        return ret


class InputNode(Node):
    MNEMONIC = 'input'
    NUM_OPS = 1

    def _emit(self):
        return [Instruction(-1, self.op1)]


class OutputNode(Node):
    MNEMONIC = 'output'
    NUM_OPS = 1

    def _emit(self):
        return [Instruction(self.op1, -1)]


def generate_code(instructions):
    labels = {}
    ctr = 0

    for insn in instructions:
        # Set the address of this instruction.
        insn.address = ctr

        # If an explicit branch address is not given, we just
        # always branch to the next instruction.
        if insn.is_instruction and insn.C is None:
            insn.C = ctr + insn.size

        # Save label, if necessary
        if insn.label is not None:
            if insn.label in labels:
                raise Exception(
                    "Duplicate label: '%s' is defined at offset %d and "
                    "%d" % (insn.label, labels[insn.label], ctr)
                )
            else:
                labels[insn.label] = ctr

        ctr += insn.size

    def get_label(s):
        if '+' in s:
            label, _, off = s.partition('+')
            off = int(off)
        else:
            label = s
            off = 0

        return labels[label] + off

    # Apply fixups
    for insn in instructions:
        if not insn.is_instruction:
            continue

        try:
            if isinstance(insn.A, str):
                if insn.A.startswith('$'):
                    insn.A = insn.address + int(insn.A[1:])
                else:
                    insn.A = get_label(insn.A)
            if isinstance(insn.B, str):
                if insn.B.startswith('$'):
                    insn.B = insn.address + int(insn.B[1:])
                else:
                    insn.B = get_label(insn.B)
            if isinstance(insn.C, str):
                if insn.C.startswith('$'):
                    insn.C = insn.address + int(insn.C[1:])
                else:
                    insn.C = get_label(insn.C)
        except KeyError as e:
            raise Exception("Label '%s' not found at address %d" % (
                e.args[0], insn.address))

    # Generate code.
    code = []
    for insn in instructions:
        code.extend(insn.code)

    start = labels.get('start', 0)
    return code, start


def pretty_print_code(code):
    ret = []
    for insn in code:
        label = ' ' * 10
        if insn.label is not None:
            label = (insn.label + ":").ljust(10)

        if isinstance(insn, Instruction):
            if insn.C is None:
                ret.append(label + "%s, %s" % (insn.A, insn.B))
            else:
                ret.append(label + "%s, %s, %s" % (insn.A, insn.B, insn.C))
        elif isinstance(insn, DataInstruction):
            ret.append(label + 'db %d' % (insn.data[0],))
            for ch in insn.data[1:]:
                ret.append('db %d' % (ch,))
        elif isinstance(insn, CommentInstruction):
            ret.append(' ' * 10 + '; ' + insn.comment)

    return '\n'.join(ret)


NODE_CLASSES = [
    SubleqNode,
    ZeroNode,
    MoveNode,
    AddNode,
    AddImmNode,
    SubNode,
    SubImmNode,
    NopNode,
    JumpNode,
    JzNode,
    BitshiftLeftNode,
    InputNode,
    OutputNode,
]

NUM_OPS = {n.MNEMONIC: n.NUM_OPS for n in NODE_CLASSES}
NUM_OPS['db'] = 1

INSTRUCTION_CLASSES = {n.MNEMONIC: n for n in NODE_CLASSES}
IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'


def parse(text):
    stripped = (x.strip() for x in text.splitlines())
    non_blank = (x for x in stripped if len(x) > 0)
    non_comment = (x for x in non_blank if not x.startswith(";"))

    ret = []
    for i, line in enumerate(non_comment):
        # Remaining in the line.
        remaining = line

        # Check for label.
        label = None
        label_match = re.match(r'^(' + IDENTIFIER + r'):\s+', remaining)
        if label_match:
            label = label_match.group(1)
            remaining = remaining[label_match.end(0):]

        # Read the first word, which will be our instruction.
        insn_match = re.match(r'^(\w+)\s+', remaining)
        if not insn_match:
            raise Exception("Syntax error: no instruction found on line %d" % (i + 1,))

        instruction = insn_match.group(1).lower()
        remaining = remaining[insn_match.end(0):]

        num_ops = NUM_OPS.get(instruction)
        if num_ops is None:
            raise Exception("Invalid instruction '%s' on line %d" % (instruction, i + 1))

        # Read this many operands.
        ops = []
        for j in range(num_ops):
            op_re = (
                r'^(' +
                r'(?P<id>' + IDENTIFIER + r'(?P<off>\+[0-2])?)|' +
                r'(?P<rel>\$[-+]?[1-9][0-9]*)|' +
                r'(?P<hex>0[xX][a-fA-F0-9]+)|' +
                r'(?P<num>[-+]?(?:[1-9][0-9]*)|0)|' +
                r"(?P<char>'.')" +
                r')'
            )
            if j != num_ops - 1:
                op_re += ',\s+'

            op_match = re.match(op_re, remaining)
            if op_match is None:
                print(line)
                print(remaining)
                raise Exception("Could not find operand %d on line %d" % (j + 1, i + 1))

            groups = op_match.groupdict()
            if groups['id'] is not None:
                # Identifier
                i = groups['id']
                if groups['off'] is not None:
                    i += groups['off']
                ops.append(i)
            if groups['rel'] is not None:
                # Relative address
                ops.append(groups['rel'])
            elif groups['hex'] is not None:
                # Hex number
                ops.append(int(groups['hex'], 16))
            elif groups['num'] is not None:
                # Regular number
                ops.append(int(groups['num']))
            elif groups['char'] is not None:
                ops.append(ord(groups['char'][1]))

            remaining = remaining[op_match.end(0):]

        if instruction == 'db':
            node = DataNode(ops[0], label=label)
        else:
            cls = INSTRUCTION_CLASSES[instruction]
            node = cls(*ops, label=label)

        ret.append(node)

    return ret


def convert_to_instructions(nodes):
    ret = []
    for node in nodes:
        if node.as_string is not None:
            ret.append(CommentInstruction(node.as_string))

        insns = node.emit()

        # TODO: convert relative displacement to instruction-relative
        ret.extend(insns)

    ret.append(DataInstruction(0, label='Z'))
    return ret


def main():
    inp = sys.stdin.read()
    nodes = parse(inp)
    #print(nodes, file=sys.stderr)

    insns = convert_to_instructions(nodes)
    print(pretty_print_code(insns), file=sys.stderr)

    code, start = generate_code(insns)
    print(start)
    print(' '.join(str(x) for x in code))

    # ins = [
    #     Instruction('data', -1, label='start'),
    #     Instruction(0, 0, -1),

    #     DataInstruction('Q', label='data'),
    # ]
    # print(generate_code(ins))


if __name__ == "__main__":
    main()
