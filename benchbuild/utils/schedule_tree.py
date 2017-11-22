""" Parsing utilities for Polly's ScheduleTree representation. """
import textwrap as t
import pyparsing as p
import logging


LOG = logging.getLogger(__name__)


class Node(object):
    def __init__(self, tok):
        self.name = tok[0]
        self.value = tok[2]
    
    def indent(self, level=0, idt=' '):
        return t.indent('"{:s}": "{:s}"'.format(self.name, self.value), level*idt)


class CoincidenceNode(object):
    def __init__(self, tok):
        self.name = tok[0]
        self.children = tok[3]

    def indent(self, level=0, idt=' '):
        ret = [str(child) for child in self.children]
        ret = ",".join(ret)

        return t.indent('"{:s}": [{:s}]'.format(self.name, ret), level*idt)

class RootNode(object):
    def __init__(self, tok):
        self.name = tok[0]
        self.children = tok[1]

    def indent(self, level=0, idt=' '):
        ret = [child.indent(level+2) for child in self.children]
        ret = ",\n".join(ret)

        return t.indent('{{\n{:s}\n}}'.format(ret), level*idt)

    def __str__(self):
        return self.indent(0)


class ChildNode(RootNode):
    def __init__(self, tok):
        self.name = tok[0]
        self.children = tok[3]

    def indent(self, level=0, idt=' '):
        ret_super = super(ChildNode, self).indent()
        ret = '"{:s}": {:s}'.format(self.name, ret_super)
        return t.indent(ret, level*idt)

class SequenceNode(object):
    def __init__(self, tok):
        self.name = tok[0]
        self.children = tok[3]

    def indent(self, level=0, idt=' '):
        ret = '"{:s}": [\n'.format(self.name)
        for child in self.children:
            ret += child.indent(level+2) + ',\n'
        ret += '\n]'
        return t.indent(ret, level * idt)

class SeqElemNode(object):
    def __init__(self, tok):
        self.val = tok[1:-1]

    def indent(self, level=0, idt=' '):
        ret = "{\n"
        ret += ",\n".join([elem.indent(level+2) for elem in self.val])
        ret += "\n}"

        return t.indent(ret, level*idt)


_CHILD       = p.Forward()
_NUMS        = p.Word(p.nums, max=1)
_QUOTED_STR  = p.QuotedString('"')

_DOMAIN      = (p.Keyword("domain")     + ":" + _QUOTED_STR)
_DOMAIN.addParseAction(Node)

_SCHEDULE    = p.Keyword("schedule")   + ":" + _QUOTED_STR
_SCHEDULE.addParseAction(Node)

_FILTER_NODE = p.Keyword("filter")     + ":" + _QUOTED_STR
_FILTER_NODE.addParseAction(Node)

_MARK        = p.Keyword("mark")       + ":" + _QUOTED_STR
_MARK.addParseAction(Node)

_PERMUTABLE  = p.Keyword("permutable") + ":" + _NUMS
_PERMUTABLE.addParseAction(Node)

_COINCIDENT  = p.Keyword("coincident") + ":" + "[" + p.Group(p.delimitedList(_NUMS)) + "]"
_COINCIDENT.addParseAction(CoincidenceNode)

_SEQ_ELEM    = "{" + p.delimitedList(_FILTER_NODE | _CHILD) + "}"
_SEQ_ELEM.addParseAction(SeqElemNode)

_SEQUENCE    = p.Keyword("sequence")   + ":" + "[" + p.Group(p.delimitedList(_SEQ_ELEM)) + "]"
_SEQUENCE.addParseAction(SequenceNode)

_CHILD_NODE  = _DOMAIN | _SCHEDULE | _SEQUENCE | _PERMUTABLE | _COINCIDENT | _MARK | _CHILD
_CHILD      << p.Keyword("child") + ":" + "{" + p.Group(p.delimitedList(_CHILD_NODE)) + "}"
_CHILD.addParseAction(ChildNode)

_ROOT_NODE   = _DOMAIN | _CHILD
_ROOT = "{" + p.Group(p.delimitedList(_ROOT_NODE)) + "}"
_ROOT.addParseAction(RootNode)

def parse_schedule_tree(tree_str):
    if tree_str is None:
        return "No Input"

    res = None
    try:
        ret = _ROOT.parseString(tree_str)
        return str(ret[0])
    except p.ParseException as ex:
        return str(ex)