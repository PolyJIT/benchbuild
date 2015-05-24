#!/usr/bin/env python

import argparse
import subprocess
import os
import sys
import time
import traceback
import re

from subprocess import Popen, PIPE
from sets import Set

src_dir = '/home/grebhahn/pprof-study/'
study_dir = '/home/grebhahn/pprof-study/'

# Command line for executing the study in a clean state
cl = ['sbatch', './pprof-array.sh', src_dir, study_dir, 'runtime', 'raw']


def parse_arguments():
    description = 'feature-runner executes a pprof-study experiment with an' \
                  'arbitrary set of configurations.'

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-C', dest='configurations', help='The filename where'
                        ' our configuration is placed in.', required=True)
    parser.add_argument('-p', action='store_true', dest='prg',
                        help='Show progress.', default=False, required=False)
    parser.add_argument('-c', action='store_true', dest='commands',
                        help='Show commands.', default=False, required=False)
    parser.add_argument('-o', dest='offset', type=int, default='0',
                        required=False)
    parser.add_argument('-x', dest='experiment', type=int, default='0',
                        required=False)
    parser.add_argument('-r', action='store_true', dest='resume',
                        help='Requeue incomplete jobs.', default=False,
                        required=False)
    parser.add_argument('-t', action='store_true', dest='throttle',
                        help='Throttle job queueing.', default=False,
                        required=False)
    arguments, argv = parser.parse_known_args()
    return arguments, argv


def die(msg):
    print 'error: ' + msg
    sys.exit(1)


def lexec(args, commandLine, msg, failOnErr=True):
    global clean_log
    level = len(traceback.format_stack())
    indent = '  ' * (level-5)

    if args.prg:
        print >> sys.stderr, indent + '\033[1;31m[ ' + msg + ' ]\033[1;m'

    if args.commands:
        print >> sys.stderr, indent + '\033[1;36m' + ' '.join(commandLine) + '\033[1;m'

    exit = subprocess.call(commandLine)
    if exit:
        print >> sys.stderr, indent + '\033[1;36m' + msg + ' FAILED. This command did not work:\033[1;m'
        print >> sys.stderr, indent + '\033[1;36m' + ' '.join(commandLine) + '\033[1;m'

    return exit


single_config = ()
single_id = ()
valid_flags = Set()
invalid_flags = Set()


def flag_valid(flag, stdout, stderr):
    lines = stderr.splitlines()
    match_str = 'opt: Unknown command line argument \'' + flag + '\'.  Try: \'opt -help\''

    for i in range(len(lines)):
        if lines[i] == match_str:
            tip_match = 'opt: Did you mean \'(?P<tip>[a-zA-Z0-9_\-\=]+)\'?'
            m = re.search(tip_match, lines[i+1])
            if m:
                tip = m.group('tip')
                return False, {'flag': flag, 'tip': tip}
    return True, None


def flags_valid(args, line):
    global valid_flags

    flags = line.split(' ')
    line_valid = True
    errors = []

    # Filter already known flags
    flags = [f for f in flags if (len(f) > 0) and
                                 (f not in valid_flags | invalid_flags)]

    # Ask opt if it likes the flag
    for flag in flags:
        cl = ['opt', '-load', 'LLVMPolly.so', flag, '-o', '/dev/null', '/dev/null']
        proc = subprocess.Popen(cl, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        fv, err = flag_valid(flag, stdout, stderr)
        line_valid = line_valid and fv
        if fv:
            valid_flags.add(flag)
        else:
            invalid_flags.add(flag)
            errors.append(err)

    return line_valid, errors


def build_config_set(args):
    global single_config
    global single_id
    if not args.configurations:
        die('configurations not set')

    config = open(args.configurations, 'r')
    cfgs = [line.replace('flags+=', '')
                .replace('\n', '')
                .replace('\r', '') for line in config if 'flags+=' in line]

    # Check arguments
    valid_cfg = True
    cfg_errors = []
    for cfg in range(len(cfgs)):
        line_valid, errors = flags_valid(args, cfgs[cfg])
        valid_cfg = valid_cfg and line_valid
        if not line_valid:
            cfg_errors.append({'num': cfg, 'errors': errors})

    if not valid_cfg:
        for err in cfg_errors:
            print err
        die('Configuration is invalid. Abort.')

    for cfg in range(len(cfgs)):
        params = cfgs[cfg].split(' ')
        for param in range(len(params)):
            p = params[param]
            if p and not ('-' == p[0]):
                params[param] = '-' + p
                cfgs[cfg] = ' '.join(params)

    configs = Set(cfgs)
    config.seek(0)
    idlist = [line.replace('ConfigID=', '')
                  .replace('\n', '')
                  .replace('\r', '') for line in config if 'ConfigID=' in line]
    ids = Set(idlist)

    for i in range(len(cfgs)):
        if i == args.experiment:
            single_config = cfgs[i]
            single_id = idlist[i]

    if not (len(ids) == len(configs)):
        die('Length of ConfigIDs (' + str(len(ids)) + ') is not equal to '
            'length of Configurations (' + str(len(configs)) + ')')

    config.close()
    print 'Got ' + str(len(configs)) + ' configurations.'
    return configs, ids


def find_results_subdir(mk_config):
    mk_config_f = open(mk_config)
    for line in mk_config_f:
        m = re.search('^RESULTS\s*=\s*(?P<results>[a-zA-Z0-9_/]+)$', line)

        if m:
            results = m.group('results')

    if len(results) > 0:
        return results

    mk_config_f.close()
    return ''


from glob import glob


def resume_queueing(args, configs, ids, src):
    if not os.path.exists(src):
        die('src_dir does not exist. stop.')

    # Read Makefile.config and search for name of RESULTS
    mk_config = os.path.join(src, 'Makefile.config')
    if not os.path.exists(mk_config):
        die('Cannot find ' + mk_config)

    res_subdir = find_results_subdir(mk_config)
    if not len(res_subdir) > 0:
        die('Could not find RESULTS variable in ' + mk_config)

    res_dir = os.path.join(src_dir, res_subdir)
    if not os.path.exists(res_dir):
        die('Found RESULTS variable but path does not exist: ' + res_dir)

    tars = glob(os.path.join(res_dir, '*.tar.gz'))
    done = []
    for tar in tars:
        h, t = os.path.split(tar)
        # Find the config number in the filename
        m = re.search('[a-zA-Z0-9]+_(?P<num>\d+)_[a-zA-Z0-9]+\.tar\.gz', t)
        if m:
            num = int(m.group('num'))
            done.append(num)
    run_config_sets(args, configs, ids, done)


def run_config_sets(args, configs, ids, exclude=[]):
    i = 0
    queued = 0

    for line, _id in zip(configs, ids):
        i += 1
        # 1. Launch the batch job
        if i > args.offset and (i not in exclude):
            lexec(args, cl + [str(i)] + ['"'+_id+'"'] + line.split(' '),
                  'Configuration ' + str(i), failOnErr=True)
            queued += 1
            if args.throttle and queued % 5 == 0:
                print 'Suspend job submission for 10min'
                time.sleep(600)
    print 'Needed to requeue ' + str(len(configs) - len(exclude)) + ' config sets'


def run_config_set(args, configs, ids, num):
    if num == 0:
        return

    if num >= len(configs):
        die('Out of bounds (configs)')
    if num >= len(ids):
        die('Out of bounds (ids)')

    lexec(args, cl + [str(num)] + ['"'+single_id+'"'] +
          single_config.split(' '),
          'Configuration ' + str(num), failOnErr=True)


def main():
    args, argv = parse_arguments()
    configs, ids = build_config_set(args)

    if args.resume:
        resume_queueing(args, configs, ids, src_dir)
        exit(0)

    if not args.experiment == 0:
        run_config_set(args, configs, ids, args.experiment)
        exit(0)
    else:
        run_config_sets(args, configs, ids)
        exit(0)

if __name__ == '__main__':
    main()
