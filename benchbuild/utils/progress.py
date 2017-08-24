"""
A progress bar based on the plumbum cli.progress.Progress bar, but
with a changed string representation to adjust the design.
"""
import sys
from plumbum import cli

class ProgressBar(cli.progress.ProgressBase):
    """Class that modifies the progress bar."""

    def __init__(self, width=None, pg_char=None, iterator=None, length=None,
                 timer=True, body=False, has_output=False, clear=True):
        """
        The default constructor of plumbums ProgressBase class with the
        additional option to set the wide of the progress bar in the
        initialisation of a ProgressBar object.
        """
        if width is None:
            width = cli.termsize.get_terminal_size(default=(0, 0))[0]
        if pg_char is None:
            pg_char = '*'
        if length is None:
            length = len(iterator)
        elif iterator is None:
            iterator = range(length)
        elif length is None and iterator is None:
            raise TypeError("Expected either an iterator or a length")

        self.width = width
        self.pg_char = pg_char
        self.length = length
        self.iterator = iterator
        self.timer = timer
        self.body = body
        self.has_output = has_output
        self.clear = clear

    def __str__(self):
        """
        The string representation of the progress bar displayed in the
        console. Almost identical as the one provided by plumbum, but adjusted
        in the width of the progress bar.
        """
        width = self.width
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
