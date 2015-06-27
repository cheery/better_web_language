from parser import grammar
import sys

def post_tuple(env, loc):
    return

def post_pass(env, loc):
    return

def post_hello(env, loc, num):
    print num.value

parser = grammar.load({}, "grammar")

for filename in sys.argv[1:]:
    parser.from_file(globals(), None, filename)
