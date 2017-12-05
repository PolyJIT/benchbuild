""" Parsing utilities for Polly's ScheduleTree representation. """
import logging
import textwrap as t
import pyparsing as p


LOG = logging.getLogger(__name__)


class Node(object):
    def __init__(self, tok):
        self.name = tok[0]
        self.value = tok[2]
    
    def indent(self, level=0, idt=' '):
        val = self.value
        if not isinstance(self.value, str):
            val = self.value.indent(1)
        return t.indent('"{:s}": "{:s}"'.format(self.name, val), level*idt)


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
        ret = []
        for r in self.children:
            ret += r.indent(level+2)
        ret = [child.indent(level+2) for child in self.children]
        ret = ",\n".join(ret)

        return t.indent('{{\n{:s}\n}}'.format(ret), level*idt)

    def __str__(self):
        return self.indent(0)


class ChildNode(RootNode):
    def __init__(self, tok):
        self.elem = tok[0]

    def indent(self, level=0, idt=' '):
        ret = self.elem.indent(level)
        return ret

class SequenceNode(object):
    def __init__(self, tok):
        self.name = tok[0]
        self.children = tok[3]

    def indent(self, level=0, idt=' '):
        ret = '"{:s}": [\n'.format(self.name)
        for child in self.children:
            ret += child.indent(0) + ',\n'
        ret += '\n]'
        return t.indent(ret, level * idt)


_NUM = p.Word(p.nums, max=1)
_NUM_LIST = p.Group(p.delimitedList(_NUM))

_STR = p.QuotedString('"')

_KW_CHILD = p.Keyword("child")
_KW_COINCIDENT = p.Keyword("coincident")
_KW_DOMAIN = p.Keyword("domain")
_KW_FILTER = p.Keyword("filter")
_KW_MARK = p.Keyword("mark")
_KW_OPTIONS = p.Keyword("options")
_KW_PERMUTABLE = p.Keyword("permutable")
_KW_SCHEDULE = p.Keyword("schedule")
_KW_EXTENSION = p.Keyword("extension")
_KW_SEQUENCE = p.Keyword("sequence")

_CHILD_NODE = p.Forward()
_ROOT = p.Forward()

_DOMAIN      = _KW_DOMAIN     + ":" + _STR
_SCHEDULE    = _KW_SCHEDULE   + ":" + _STR
_FILTER      = _KW_FILTER     + ":" + _STR
_MARK        = _KW_MARK       + ":" + _STR
_PERMUTABLE  = _KW_PERMUTABLE + ":" + _NUM
_COINCIDENT  = _KW_COINCIDENT + ":" + "[" + _NUM_LIST + "]"
_OPTIONS     = _KW_OPTIONS    + ":" + _STR
_EXTENSION   = _KW_EXTENSION  + ":" + _STR

_SEQ_ELEM_LIST = p.delimitedList(_ROOT)
_SEQUENCE    = _KW_SEQUENCE + ":" + "[" + p.Group(p.delimitedList(_ROOT)) + "]"
_CHILD = _KW_CHILD + ":" + _ROOT
_CHILD_NODE  << (
                 _CHILD      |
                 _COINCIDENT |
                 _DOMAIN     |
                 _EXTENSION  |
                 _FILTER     |
                 _MARK       |
                 _OPTIONS    |
                 _PERMUTABLE |
                 _SCHEDULE   |
                 _SEQUENCE
                )
_ROOT << ("{" + p.Group(p.delimitedList(_CHILD_NODE)) + "}")

_CHILD.addParseAction(Node)
_CHILD_NODE.addParseAction(ChildNode)
_COINCIDENT.addParseAction(CoincidenceNode)
_DOMAIN.addParseAction(Node)
_FILTER.addParseAction(Node)
_MARK.addParseAction(Node)
_OPTIONS.addParseAction(Node)
_PERMUTABLE.addParseAction(Node)
_ROOT.addParseAction(RootNode)
_EXTENSION.addParseAction(Node)
_SCHEDULE.addParseAction(Node)
_SEQUENCE.addParseAction(SequenceNode)

def parse_schedule_tree(tree_str):
    if tree_str is None:
        return "No Input"

    res = None
    try:
        ret = _ROOT.parseString(tree_str)
        return str(ret[0])
    except p.ParseException as ex:
        LOG.warning("Failed to parse:")
        LOG.warning(str(ex))
        LOG.warning(tree_str)
        return None