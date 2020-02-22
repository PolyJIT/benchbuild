""" Parsing utilities for Polly's ScheduleTree representation. """
import logging
import textwrap as t

import attr
import pyparsing as p

LOG = logging.getLogger(__name__)


@attr.s
class Node:
    tok = attr.ib()

    def indent(self, level=0, idt=' '):
        val = self.tok[2]
        if not isinstance(self.tok[2], str):
            val = self.tok[2].indent(1)
        return t.indent('"{:s}": "{:s}"'.format(self.tok[0], val), level * idt)


@attr.s
class CoincidenceNode(Node):

    def indent(self, level=0, idt=' '):
        ret = [str(child) for child in self.tok[3]]
        ret = ",".join(ret)

        return t.indent('"{:s}": [{:s}]'.format(self.tok[0], ret), level * idt)


@attr.s
class RootNode(Node):

    def indent(self, level=0, idt=' '):
        ret = []
        ret = [child.indent(level + 2) for child in self.tok[1]]
        ret = ",\n".join(ret)

        return t.indent('{{\n{:s}\n}}'.format(ret), level * idt)

    def __str__(self):
        return self.indent(0)


@attr.s
class ChildNode(Node):

    def indent(self, level=0, idt=' '):
        ret = self.tok[0].indent(level)
        return ret


@attr.s
class SequenceNode(Node):

    def indent(self, level=0, idt=' '):
        ret = '"{:s}": [\n'.format(self.tok[0])
        for child in self.tok[3]:
            ret += child.indent(0) + ',\n'
        ret += '\n]'
        return t.indent(ret, level * idt)


NUM = p.Word(p.nums, max=1)
NUM_LIST = p.Group(p.delimitedList(NUM))

STR = p.QuotedString('"')

KW_CHILD = p.Keyword("child")
KW_COINCIDENT = p.Keyword("coincident")
KW_DOMAIN = p.Keyword("domain")
KW_FILTER = p.Keyword("filter")
KW_MARK = p.Keyword("mark")
KW_OPTIONS = p.Keyword("options")
KW_PERMUTABLE = p.Keyword("permutable")
KW_SCHEDULE = p.Keyword("schedule")
KW_EXTENSION = p.Keyword("extension")
KW_SEQUENCE = p.Keyword("sequence")

CHILD_NODE = p.Forward()
ROOT = p.Forward()

DOMAIN = KW_DOMAIN + ":" + STR
SCHEDULE = KW_SCHEDULE + ":" + STR
FILTER = KW_FILTER + ":" + STR
MARK = KW_MARK + ":" + STR
PERMUTABLE = KW_PERMUTABLE + ":" + NUM
COINCIDENT = KW_COINCIDENT + ":" + "[" + NUM_LIST + "]"
OPTIONS = KW_OPTIONS + ":" + STR
EXTENSION = KW_EXTENSION + ":" + STR

SEQ_ELEM_LIST = p.delimitedList(ROOT)
SEQUENCE = KW_SEQUENCE + ":" + "[" + p.Group(p.delimitedList(ROOT)) + "]"
CHILD = KW_CHILD + ":" + ROOT
CHILD_NODE << (CHILD | COINCIDENT | DOMAIN | EXTENSION | FILTER | MARK |
               OPTIONS | PERMUTABLE | SCHEDULE | SEQUENCE)
ROOT << ("{" + p.Group(p.delimitedList(CHILD_NODE)) + "}")

CHILD.addParseAction(Node)
CHILD_NODE.addParseAction(ChildNode)
COINCIDENT.addParseAction(CoincidenceNode)
DOMAIN.addParseAction(Node)
FILTER.addParseAction(Node)
MARK.addParseAction(Node)
OPTIONS.addParseAction(Node)
PERMUTABLE.addParseAction(Node)
ROOT.addParseAction(RootNode)
EXTENSION.addParseAction(Node)
SCHEDULE.addParseAction(Node)
SEQUENCE.addParseAction(SequenceNode)


def parse_schedule_tree(tree_str):
    if tree_str is None:
        return "No Input"

    try:
        ret = ROOT.parseString(tree_str)
        return str(ret[0])
    except p.ParseException as ex:
        LOG.warning("Failed to parse:")
        LOG.warning(str(ex))
        LOG.warning(tree_str)
        return None
