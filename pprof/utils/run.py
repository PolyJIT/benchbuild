"""
Experiment helpers
"""


def handle_stdin(cmd, kwargs):
    """
    Handle stdin for wrapped runtime executors.
    :return:
        A new plumbum command that deals with stdin redirection, if needed.
    """
    assert isinstance(kwargs, dict)
    import sys

    has_stdin = kwargs.get("has_stdin", False)
    if has_stdin:
        run_cmd = (cmd < sys.stdin)
    else:
        run_cmd = cmd

    return run_cmd


def fetch_time_output(marker, format_s, ins):
    """
    Fetch the output /usr/bin/time from a

    :marker:
        The marker that limits the time output
    :format_s:
        The format string used to parse the timings
    :ins:
        A list of lines we look for the output.

    :returns:
        A list of timing tuples
    """
    from parse import parse

    timings = [x for x in ins if marker in x]
    res = [parse(format_s, t) for t in timings]
    return filter(None, res)
