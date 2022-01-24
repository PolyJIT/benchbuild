"""
Likwid helper functions.

Extract information from likwid's CSV output.
"""
import typing as tp


def fetch_cols(fstream: tp.IO[str], split_char: str = ',') -> tp.List[str]:
    """
    Fetch columns from likwid's output stream.

    Args:
        fstream: The filestream with likwid's output.
        split_car (str): The character we split on, default ','

    Returns (list(str)):
        A list containing the elements of fstream, after splitting at
        split_char.
    """
    return fstream.readline().strip().split(split_char)


def read_struct(fstream: tp.IO[str]) -> tp.Optional[tp.Dict[str, tp.List[str]]]:
    """
    Read a likwid struct from the text stream.

    Args:
        fstream: Likwid's filestream.

    Returns (dict(str: str)):
        A dict containing all likwid's struct info as key/value pairs.
    """
    line = fstream.readline().strip()
    fragments = line.split(",")
    fragments = [x for x in fragments if x is not None]
    partition = {}
    if not len(fragments) >= 3:
        return None

    partition["struct"] = fragments[0]
    partition["info"] = fragments[1]
    partition["num_lines"] = fragments[2]

    struct = None
    if partition is not None and partition["struct"] == "STRUCT":
        num_lines = int(partition["num_lines"].strip())
        struct = {}
        for _ in range(num_lines):
            cols = fetch_cols(fstream)
            struct.update({cols[0]: cols[1:]})
    return struct


def read_table(fstream: tp.IO[str]) -> tp.Optional[tp.Dict[str, tp.List[str]]]:
    """
    Read a likwid table info from the text stream.

    Args:
        fstream: Likwid's filestream.

    Returns (dict(str: str)):
        A dict containing likwid's table info as key/value pairs.
    """
    pos = fstream.tell()
    line = fstream.readline().strip()
    fragments = line.split(",")
    fragments = [x for x in fragments if x is not None]
    partition = {}
    if not len(fragments) >= 4:
        return None

    partition["table"] = fragments[0]
    partition["group"] = fragments[1]
    partition["set"] = fragments[2]
    partition["num_lines"] = fragments[3]

    struct = None
    if partition is not None and partition["table"] == "TABLE":
        num_lines = int(partition["num_lines"].strip())
        struct = {}
        header = fetch_cols(fstream)

        struct.update({header[0]: header[1:]})
        for _ in range(num_lines):
            cols = fetch_cols(fstream)
            struct.update({cols[0]: cols[1:]})
    else:
        fstream.seek(pos)

    return struct


def read_structs(
    fstream: tp.IO[str]
) -> tp.Generator[tp.Optional[tp.Dict[str, tp.List[str]]], None, None]:
    """
    Read all structs from likwid's file stream.

    Args:
        fstream: Likwid's output file stream.

    Returns:
        A generator that can be used to iterate over all structs in the
        fstream.
    """
    struct = read_struct(fstream)
    while struct is not None:
        yield struct
        struct = read_struct(fstream)


def read_tables(
    fstream: tp.IO[str]
) -> tp.Generator[tp.Optional[tp.Dict[str, tp.List[str]]], None, None]:
    """
    Read all tables from likwid's file stream.

    Args:
        fstream: Likwid's output file stream.

    Returns:
        A generator that can be used to iterate over all tables in the fstream.
    """
    table = read_table(fstream)
    while table is not None:
        yield table
        table = read_table(fstream)


def get_measurements(
    region: str,
    core_info,
    data,
    extra_offset: int = 0
) -> tp.List[tp.Tuple[str, str, str, str]]:
    """
    Get the complete measurement info from likwid's region info.

    Args:
        region: The region we took a measurement in.
        core_info: The core information.
        data: The raw data.
        extra_offset (int): default = 0

    Returns (list((region, metric, core, value))):
        A list of measurement tuples, a tuple contains the information about
        the region, the metric, the core and the actual value.
    """
    measurements = []
    clean_core_info = [x for x in core_info if x]
    cores = len(clean_core_info)
    for k in data:
        if k not in ["1", "Region Info", "Event", "Metric", "CPU clock"]:
            slot = data[k]
            for i in range(cores):
                core = core_info[i]
                idx = extra_offset + i
                if core and slot[idx]:
                    measurements.append((region, k, core, slot[idx]))

    return measurements


def perfcounters(infile: str) -> tp.List[tp.Tuple[str, str, str, str]]:
    """
    Get a complete list of all measurements.

    Args:
        infile: The filestream containing all likwid output.

    Returns:
        A list of all measurements extracted from likwid's file stream.
    """
    measurements = []
    with open(infile, 'r') as in_file:
        read_struct(in_file)
        structs = [rs for rs in read_structs(in_file) if rs is not None]
        for region_struct in structs:
            region = region_struct["1"][1]
            core_info = region_struct["Region Info"]
            measurements += \
                get_measurements(region, core_info, region_struct)

            tables = [ts for ts in read_tables(in_file) if ts is not None]
            for table_struct in tables:
                evt_core_info: tp.Optional[tp.List[str]] = None
                if "Event" in table_struct:
                    offset = 1
                    evt_core_info = table_struct["Event"][offset:]
                    measurements += get_measurements(
                        region, evt_core_info, table_struct, offset
                    )
                elif "Metric" in table_struct:
                    evt_core_info = table_struct["Metric"]
                    measurements += get_measurements(
                        region, evt_core_info, table_struct
                    )
    return measurements
