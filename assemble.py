#!/usr/bin/env python

from __future__ import print_function

import sys
import string

from pyparsing import (
    CaselessLiteral,
    CharsNotIn,
    Combine,
    LineEnd,
    LineStart,
    Literal,
    Optional,
    Word,
    ZeroOrMore,
    alphanums,
    alphas,
    nums,
    restOfLine,
)


# Numbers
DECIMAL_NUM = Word('-+'+nums, nums).setParseAction(lambda s, loc, toks: int(toks[0]))
HEX_CHARS = nums + 'abcdefABCDEF'
HEX_BEGIN = Optional(Literal('-') | Literal('+')) + CaselessLiteral('0x')
HEX_NUM = Combine(HEX_BEGIN + Word(HEX_CHARS)).setParseAction(lambda s, loc, toks: int(toks[0], 16))
NUM = HEX_NUM | DECIMAL_NUM

# Identifiers
IDENTIFIER = Word(alphas, alphanums + "_")

# Label
LABEL = (IDENTIFIER + Literal(':').suppress())

# Data
DATA_CMD = Combine(Literal('d') + (Literal('b') | Literal('s')))
CHAR_LITERAL = (
    Literal("'").suppress() +
    CharsNotIn("'", exact=1).setParseAction(lambda s, loc, toks: ord(toks[0])) +
    Literal("'").suppress()
)
DATA_LITERAL = CHAR_LITERAL | NUM
DATA = DATA_CMD.setResultsName('dataCmd') + DATA_LITERAL.setResultsName('dataValue')

# Operand - can be either a number (optionally relative), or an identifier
OPERAND = (
    NUM |
    IDENTIFIER
)

# Line
SUBLEQ_LINE = (
    LineStart() +

    # Optional label - label:
    Optional(LABEL.setResultsName("label")
                  .setParseAction(lambda s, loc, toks: toks[0])
    ) +

    # Command or data
    (
        DATA |
        (
            Optional(Literal('$').setResultsName('relA')) + OPERAND.setResultsName('A') + Literal(",") +
            Optional(Literal('$').setResultsName('relB')) + OPERAND.setResultsName('B') +
            Optional(Literal(",") + Optional(Literal('$').setResultsName('relC')) + OPERAND.setResultsName('C'))
         )
    ) +

    # Comment - runs until end-of-line
    Optional(
        Literal(";") + Word(alphanums + string.punctuation)
    )

    + LineEnd()
)

HIGH_LINE = (
    LineStart() +

    # Optional label - label:
    Optional(LABEL.setResultsName("label")
                  .setParseAction(lambda s, loc, toks: toks[0])
    ) +

    (
        DATA |
        (
            # Command
            Word(alphas).setResultsName("command") +

            # Operand(s)
            Optional(Literal('$').setResultsName('relA')) + OPERAND.setResultsName('A') +
            Optional(Literal(",") + Optional(Literal('$').setResultsName('relB')) + OPERAND.setResultsName('B'))
        )
    ) +

    # Comment - runs until end-of-line
    Optional(
        Literal(";") + Word(alphanums + string.punctuation)
    )

    + LineEnd()
)


def is_numeric(s):
    try:
        int(s)
        return True
    except ValueError:
        return False



def assemble(text):
    stripped = (x.strip() for x in text.splitlines())
    non_blank = (x for x in stripped if len(x) > 0)
    non_comment = (x for x in non_blank if not x.startswith(";"))

    code = []
    fixups = []
    labels = {}

    for line in non_comment:
        res = SUBLEQ_LINE.parseString(line)
        pos = len(code)

        if 'label' in res:
            labels[res['label']] = pos

        # Emit code or data.
        if 'dataCmd' in res:
            code.append(res['dataValue'])
        else:
            a = res['A']
            b = res['B']
            c = res.get('C', pos + 3)

            def add_op(offset, op):
                if is_numeric(op):
                    code.append(op)
                elif op[0] == '$' and is_numeric(op[1:]):
                    code.append(op)
                else:
                    if op in labels:
                        code.append(labels[op])
                    else:
                        code.append(-2)
                        fixups.append((offset, op))

            add_op(pos, a)
            add_op(pos + 1, b)
            add_op(pos + 2, c)

    for offset, label in fixups:
        #print("[asm] Reloc %d --> label '%s' (%d)" % (offset, label, labels[label]),
        #      file=sys.stderr)
        code[offset] = labels[label]

    start = labels['start']

    print("[asm] Code = %r" % (code,), file=sys.stderr)
    print("[asm] Start = %d" % (start,), file=sys.stderr)
    return code, start


def assemble_high(text):
    stripped = (x.strip() for x in text.splitlines())
    non_blank = (x for x in stripped if len(x) > 0)
    non_comment = (x for x in non_blank if not x.startswith(";"))

    class g(object):
        curr_label = None
        label_i = 0

    lines = [
        'Z: db 0',
    ]
    def add_line(s):
        s = '\t' + s
        if s.lstrip().startswith(';'):
            lines.append(s)
        else:
            if g.curr_label is not None:
                s = g.curr_label + ': ' + s
            lines.append(s)
            g.curr_label = None

    def set_label(l):
        g.curr_label = l

    def temp_label():
        lname = "tmp__%d" % (g.label_i,)
        g.label_i += 1
        return lname

    for line in non_comment:
        res = HIGH_LINE.parseString(line)
        curr = ""

        if 'label' in res:
            set_label(res['label'])

        if 'dataCmd' in res:
            add_line("%s %d" % (res['dataCmd'], res['dataValue']))
            continue

        command = res['command'].lower()
        op1 = res['A']
        op2 = res.get('B')

        if command == 'jmp':
            add_line('; jmp %s' % (op1,))
            add_line('Z, Z, %s' % (op1,))
        elif command == 'zero':
            add_line('; zero %s' % (op1,))
            add_line('%s, %s' % (op1, op1))
        elif command == 'mov':
            add_line('; mov %s, %s' % (op1, op2))
            add_line('%s, %s' % (op2, op2))
            add_line('%s, Z' % (op1,))
            add_line('Z, %s' % (op2,))
            add_line('Z, Z')
        elif command == 'add':
            add_line('; add %s, %s' % (op1, op2))
            add_line('%s, Z' % (op1,))
            add_line('Z, %s' % (op2,))
            add_line('Z, Z')
        elif command == 'sub':
            add_line('; sub %s, %s' % (op1, op2))
            add_line('%s, %s' % (op1, op2))
        elif command == 'jz':
            add_line('; jz %s, %s' % (op1, op2))
            add_line('%s, Z, $+6' % (op1,))
            add_line('Z, Z, $+9')
            add_line('Z, Z')
            add_line('Z, %s, %s' % (op1, op2))


        lines.append('')

    return '\n'.join(lines)


def main():
    low_code = sys.stdin.read()
    if len(sys.argv) > 1 and sys.argv[1] == '-h':
        low_code = assemble_high(low_code)
        print(low_code, file=sys.stderr)

    code, start = assemble(low_code)
    print("%d" % (start,))
    print("%s" % (' '.join(str(x) for x in code),))


if __name__ == "__main__":
    main()
