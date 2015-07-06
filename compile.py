from block import Local, VReg, Block
from functools import partial
from parser import grammar
import json, struct, sys

def post_pass(env, loc, val):
    return val

def post_concat(env, loc, lhs, rhs):
    return lhs + rhs

def post_call(env, loc, callee, arguments):
    callee_result = callee.result
    block = callee
    for arg in arguments:
        block += arg
    args = [arg.result for arg in arguments]
    block.result = VReg()
    block.op(['call', block.result, callee_result, args])
    return block

def post_lookup(env, loc, symbol):
    block = Block(loc)
    block.result = Local(symbol.value)
    block.uses.append(block.result)
    block.contents.append(block.result)
    return block

def post_constant_int(env, loc, const):
    block = Block(loc)
    block.result = VReg()
    block.op(['int32', block.result, int(const.value)])
    return block

def post_constant_string(env, loc, const):
    block = Block(loc)
    block.result = VReg()
    block.op(['string', block.result, const.value])
    return block

def post_empty(env, loc):
    return []

def post_first(env, loc, num):
    return [num]

def post_append(env, loc, seq, num):
    seq.append(num)
    return seq

def post_function(env, loc, body):
    closure = new_closure(env, body)
    block = Block(loc)
    block.result = VReg()
    block.op(['closure', block.result, closure])
    return block

def post_assign(env, loc, symbol, expr):
    expr.defs[symbol.value] = expr.result
    return expr

# not sure what to do with this.
#def post_assign(env, loc, symbol, expr):
#    env.append(['setglobal', symbol.value, expr])

parser = grammar.load({}, "grammar")
with open("runtime/optable.json") as fd:
    optable = json.load(fd)
enc = {}
for op in optable:
    enc[op[1]] = op[0], op[2]

def vreg_index(vreg):
    if isinstance(vreg, VReg):
        return struct.pack('B', vreg.index)
    if isinstance(vreg, Local):
        assert vreg.link is not None, vreg.name
        return vreg_index(vreg.link)
    assert False, vreg

tptab = {
    "dst": vreg_index,
    "src": vreg_index,
    "int32": partial(struct.pack, 'i'),
    "string": (lambda x: (
        struct.pack('H', len(x)) +
        x.encode('utf-8'))),
    "src*": (lambda xs:
        struct.pack('H', len(xs)) +
        ''.join(vreg_index(x) for x in xs)),
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

class Closure(object):
    def __init__(self, body):
        self.nonlocals = body.uses
        self.blocks = postorder(body.first)

def new_closure(env, body):
    body.result = VReg()
    body.op(['int32', body.result, 0])
    body.op(['return', body.result])
    closure = Closure(body)
    env.append(closure)
    return closure

# XXX: won't possibly create a postorder function from this
# even on a good day.
def postorder(current):
    visited = set()
    stack = []
    while current and current not in visited:
        visited.add(current)
        stack.append(current)
        current = current.goto # XXX: queue later
    for index, block in enumerate(stack):
        block.index = index
    return stack

def blocks_encode(blocks):
    code = ''
    regc = 0
    for block in blocks:
        assert block.offset is None or block.offset == len(code), (block.offset, len(code))
        block.offset = len(code)
        for i, op in enumerate(block.contents):
            if isinstance(op, Local):
                if op.link is not None:
                    continue
                op.link = VReg()
                op = ['getglobal', op.link, op.name]
                block.contents[i] = op
            for item in op:
                if isinstance(item, VReg) and not item.selected:
                    item.selected = True
                    item.index = regc
                    regc += 1
            code += op_encode(op)
    return code, regc

for filename in sys.argv[1:]:
    closures = []
    block = parser.from_file(globals(), closures, filename)
    new_closure(closures, block)

    closures.reverse()
    for function_id, closure in enumerate(closures):
        closure.function_id = function_id
        if False:
            print function_id
            for block in closure.blocks:
                for line in block.contents:
                    print "  ", line
    with open(filename + '.bc', 'w') as fd:
        fd.write(struct.pack('I', len(closures)))
        for closure in closures:
            code, regc = blocks_encode(closure.blocks)
            bytelength = len(code)
            fd.write(struct.pack('II', bytelength, regc))
            code, regc = blocks_encode(closure.blocks)
            fd.write(code)
