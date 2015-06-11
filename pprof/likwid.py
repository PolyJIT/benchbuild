#!/usr/bin/env python

import argparse
import os
import regex


def extract_region(line, region):
    region_pattern = regex.compile('Region: (?P<name>[\w.:]+)')
    m = region_pattern.search(line)
    if m:
        return m.group('name')
    return region


def extract_line_info(line):
    line_pattern = regex.compile('(?P<name>[\w\(\)\[\].: ]+),(.+)')
    res = line_pattern.search(line)
    if res:
        return res.group('name'), res.group(2).split(',')
    return '', None


core_info_pattern = regex.compile('(Event|Metric|Region Info),(.+)')


def extract_core_info(line):
    res = regex.search(core_info_pattern, line)
    if res:
        return res.group(2).split(',')
    return None

run_info_separator = regex.compile(
    '-------------------------------------------------------------')


def extract_run_info(infile):
    header = []
    found = 0
    for line in infile:
        if found == 3:
            return header

        m = run_info_separator.search(line)
        if m and found < 3:
            found = found + 1
        else:
            header.append(line)

    return header


def find_first_region(infile):
    region = ''
    for line in infile:
        ri = extract_region(line, region)
        if ri != region:
            return ri
    return region


def get_likwid_perfctr(infile):
    metrics = []
    region = ''
    core_info = []

    with open(infile, 'r') as fileIn:
        header = extract_run_info(fileIn)

        # Let's hope the stdout of the application does not screw us.
        region = find_first_region(fileIn)

        for line in fileIn:
            ri = extract_region(line, region)
            if ri != region:
                region = ri
                continue

            ci = extract_core_info(line)
            if ci:
                core_info = ci
                continue

            name, li = extract_line_info(line)
            if li:
                eltstr = ''
                if len(region) > 0:
                    eltstr = region + ','
                for i in range(len(li)):
                    element = (region, name, core_info[i], li[i])
                    metrics.append(element)

    return metrics


def to_db(run_id, measurements):
    from pprof.utils.db import get_db_connection
    conn = get_db_connection()

    sql_insert = ("INSERT INTO likwid (region, metric, core, value, run_id) "
                  "VALUES (%s, %s, %s, %s, %s)")
    with conn.cursor() as c:
        for (region, name, core, value) in measurements:
            c.execute(sql_insert, (region, name, core, value, run_id))
    conn.commit()
