from functools import partial
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

def post_empty(env, loc):
    return []

def post_first(env, loc, num):
    return [num]

def post_append(env, loc, seq, num):
    seq.append(num)
    return seq

def pre_function(env, loc):
    return env.closure()

def post_function(env, loc, block):
    dst = env.getreg()
    env.append(['int32', dst, 0])
    env.append(['return', dst])
    parent = env.parent
    dst = parent.getreg()
    parent.append(['closure', dst, env.close()])
    return dst

def post_call(env, loc, callee, arguments):
    dst = env.getreg()
    env.append(['call'] +
        [dst, callee,
         [arg for arg in arguments]])
    return dst

def post_assign(env, loc, symbol, expr):
    env.append(['setglobal', symbol.value, expr])

def post_lookup(env, loc, symbol):
    dst = env.getreg()
    env.append(['getglobal', dst, symbol.value])
    return dst

def post_constant_int(env, loc, const):
    dst = env.getreg()
    env.append(['int32', dst, int(const.value)])
    return dst

def post_constant_string(env, loc, const):
    dst = env.getreg()
    env.append(['string', dst, const.value])
    return dst

parser = grammar.load({}, "grammar")
with open("runtime/optable.json") as fd:
    optable = json.load(fd)
enc = {}
for op in optable:
    enc[op[1]] = op[0], op[2]

tptab = {
    "dst": partial(struct.pack, 'B'),
    "src": partial(struct.pack, 'B'),
    "int32": partial(struct.pack, 'i'),
    "string": (lambda x: (
        struct.pack('H', len(x)) +
        x.encode('utf-8'))),
    "src*": (lambda xs:
        struct.pack('H', len(xs)) +
        ''.join(struct.pack('B', x) for x in xs)),
    "function_id": (lambda xs:
        struct.pack('H', xs.function_id)),
}

def op_encode(item):
    name = item[0]
    opcode, optypes = enc[name]
    assert len(optypes) == len(item) - 1
    data = struct.pack('B', opcode)
    for tp, val in zip(optypes, item[1:]):
        data += tptab[tp](val)
    return data

class Env(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.closures = []
        self.sequence = []
        self.regc = 0
        self.function_id = None

    def __len__(self):
        return len(self.sequence)

    def __iter__(self):
        return iter(self.sequence)

    def append(self, item):
        self.sequence.append(item)

    def getreg(self):
        reg = self.regc
        self.regc += 1
        return reg

    def closure(self):
        env = Env(self)
        self.closures.append(env)
        return env

    def close(self):
        return self

    def closures_list(self, out=None):
        out = [] if out is None else out
        out.append(self)
        for closure in self.closures:
            closure.closures_list(out)
        return out

for filename in sys.argv[1:]:
    env = Env()
    parser.from_file(globals(), env, filename)
    dst = env.getreg()
    env.append(['int32', dst, 0])
    env.append(['return', dst])
    entry_closure = env.close()

    closures = entry_closure.closures_list()
    for function_id, closure in enumerate(closures):
        closure.function_id = function_id
        if False:
            print function_id
            for line in closure:
                print "  ", line
    with open(filename + '.bc', 'w') as fd:
        fd.write(struct.pack('I', len(closures)))
        for env in closures:
            bytelength = len(''.join(op_encode(item)
                for item in env))
            fd.write(struct.pack('II', bytelength, env.regc))
            for item in env:
                fd.write(op_encode(item))
