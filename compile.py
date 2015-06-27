from parser import grammar
import json, struct, sys

def post_tuple(env, loc):
    return

def post_pass(env, loc, val):
    return

def post_hello(env, loc, num):
    env.append(int(num.value))

def post_op(env, loc, opname, nums):
    env.append([opname.value] + [int(num.value) for num in nums])

def post_first(env, loc, num):
    return [num]

def post_append(env, loc, seq, num):
    seq.append(num)
    return seq

parser = grammar.load({}, "grammar")
with open("runtime/optable.json") as fd:
    optable = json.load(fd)
enc = {}
for op in optable:
    enc[op[1]] = op[0], op[2]

tptab = {'dst': 'B', 'src': 'B', 'int32': 'i'}

def op_encode(item):
    name = item[0]
    opcode, optypes = enc[name]
    assert len(optypes) == len(item) - 1
    data = struct.pack('B', opcode)
    for tp, val in zip(optypes, item[1:]):
        data += struct.pack(tptab[tp], val)
    return data

for filename in sys.argv[1:]:
    reg_count = 10
    env = []
    parser.from_file(globals(), env, filename)

    with open(filename + '.bc', 'w') as fd:
        fd.write(struct.pack('I', reg_count))
        for item in env:
            if isinstance(item, int):
                fd.write(struct.pack('B', item))
            else:
                fd.write(op_encode(item))
