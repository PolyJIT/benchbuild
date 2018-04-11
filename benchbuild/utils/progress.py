"""
A progress bar based on the plumbum cli.progress.Progress bar, but
with a changed string representation to adjust the design.
"""
import sys

import attr
from plumbum import cli

@attr.s
class ProgressBar(cli.progress.ProgressBase):
    """Class that modifies the progress bar."""

    width = attr.ib(default=cli.termsize.get_terminal_size(default=(0, 0))[0])
    pg_char = attr.ib(default='*')
    iterator = attr.ib(default=None)
    length = attr.ib(default=None)
    timer = attr.ib(default=True)
    body = attr.ib(default=False)
    has_output = attr.ib(default=False)
    clear = attr.ib(default=True)
    value = attr.ib(default=None)
    width = attr.ib(default=None)

    def __attrs_post_init__(self):
        if self.length and (self.iterator is None):
            self.iterator = range(self.length)
        if self.iterator and (self.length is None):
            self.length = len(self.iterator)

    def __str__(self):
        """
        The string representation of the progress bar displayed in the
        console. Almost identical as the one provided by plumbum, but adjusted
        in the width of the progress bar.
        """
        width = self.width
        if self.length == 0:
            percent = 1
        else:
            percent = max(self.value, 0)/self.length
        pg_char = self.pg_char
        ending = ' ' + (self.str_time_remaining()
                        if self.timer
                        else '{0} of {1} complete'.format(self.value,
                                                          self.length))
        if width - len(ending) < 10 or self.has_output:
            self.width = 0
            if self.timer:
                return "{0:.0%} complete: {1}".format(percent,
                                                      self.str_time_remaining())
            else:
                return "{0:.0%} complete".format(percent)

        else:
            num_of_chars = int(percent*self.width)
            pbar = '[' + pg_char*num_of_chars + \
                   ' '*(self.width-num_of_chars) + ']' + ending

        str_percent = ' {0:.0%} '.format(percent)

        return pbar[:self.width//2 - 2] \
                    + str_percent + pbar[self.width//2+len(str_percent) - 2:]

    def start(self):
        """Completely identical to the Progress class from plumbum."""
        super(ProgressBar, self).start()
        self.display()

    def done(self):
        """Completely identical to the Progress class from plumbum."""
        self.value = self.length
        self.display()
        if self.clear and not self.has_output:
            print("\r", len(str(self)) * " ", "\r", end='', sep='')
        else:
            print()

    def display(self):
        """Completely identical to the Progress class from plumbum."""
        disptxt = str(self)
        if self.width == 0 or self.has_output:
            print(disptxt)
        else:
            print("\r", end='')
            print(disptxt, end='')
            sys.stdout.flush()
