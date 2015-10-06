#!/usr/bin/env python


def fetch_cols(fstream, split_char=','):
    return fstream.readline().strip().split(split_char)


def read_struct(fstream):
    line = fstream.readline().strip()
    fragments = line.split(",")
    fragments = [x for x in fragments if x is not None]
    p = dict()
    if not len(fragments) >= 3:
        return None

    p["struct"] = fragments[0]
    p["info"] = fragments[1]
    p["num_lines"] = fragments[2]

    struct = None
    if p is not None and p["struct"] == "STRUCT":
        num_lines = int(p["num_lines"].strip())
        struct = {}
        for _ in range(num_lines):
            cols = fetch_cols(fstream)
            struct.update({cols[0]: cols[1:]})
    return struct


def read_table(fstream):
    pos = fstream.tell()
    line = fstream.readline().strip()
    fragments = line.split(",")
    fragments = [x for x in fragments if x is not None]
    p = dict()
    if not len(fragments) >= 4:
        return None

    p["table"] = fragments[0]
    p["group"] = fragments[1]
    p["set"] = fragments[2]
    p["num_lines"] = fragments[3]

    struct = None
    if p is not None and p["table"] == "TABLE":
        num_lines = int(p["num_lines"].strip())
        struct = {}
        header = fetch_cols(fstream)

        struct.update({header[0]: header[1:]})
        for _ in range(num_lines):
            cols = fetch_cols(fstream)
            struct.update({cols[0]: cols[1:]})
    else:
        fstream.seek(pos)

    return struct


def read_structs(fstream):
    struct = read_struct(fstream)
    while struct is not None:
        yield struct
        struct = read_struct(fstream)


def read_tables(fstream):
    table = read_table(fstream)
    while table is not None:
        yield table
        table = read_table(fstream)

def get_measurements(region, core_info, data, extra_offset = 0):
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


def get_likwid_perfctr(infile):
    measurements = []
    with open(infile, 'r') as in_file:
        read_struct(in_file)
        for region_struct in read_structs(in_file):
            region = region_struct["1"][1]
            core_info = region_struct["Region Info"]
            measurements += \
                get_measurements(region, core_info, region_struct)

            for table_struct in read_tables(in_file):
                core_info = None
                if "Event" in table_struct:
                    offset = 1
                    core_info = table_struct["Event"][offset:]
                    measurements += get_measurements(region, core_info,
                                                     table_struct, offset)
                elif "Metric" in table_struct:
                    core_info = table_struct["Metric"]
                    measurements += get_measurements(region, core_info,
                                                     table_struct)
    return measurements
