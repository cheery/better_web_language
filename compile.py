from parser import grammar
import json, sys

def post_tuple(env, loc):
    return

def post_pass(env, loc):
    return

def post_hello(env, loc, num):
    env.append(num.value)

parser = grammar.load({}, "grammar")

for filename in sys.argv[1:]:
    env = []
    parser.from_file(globals(), env, filename)

    with open(filename + '.bc', 'w') as fd:
        json.dump(env, fd)
