class Block(object):
    def __init__(self, loc):
        self.loc = loc
        self.first = self
        self.contents = []
        self.uses = []
        self.defs = dict()
        self.link = []
        self.goto = None
        self.result = None
        self.offset = None
        self.index = 0

    def op(self, seq):
        self.contents.append(seq)

    def __add__(self, other):
        assert self.goto is None
        self.goto = other.first
        for use in other.uses:
            if use.name in self.defs:
                use.link = self.defs[use.name]
            else:
                self.uses.append(use)
        other.uses = self.uses
        other.defs.update(self.defs)
        other.first = self.first
        return other

class VReg(object):
    def __init__(self):
        self.index = 0
        self.selected = False

class Local(object):
    def __init__(self, name):
        self.name = name
        self.link = None

    def __repr__(self):
        if self.link is None:
            return self.name + '[*]'
        return self.name

