"""
A script to run the whole scraping from command line, using command line arguments.

Also implements option to run spiders in parallel by invoking separate python processes for each spider.

Run e.g. as `python3 run.py -s 3 careerjet aecom-cw halfords-cw`

Or `python3 run.py -s 5 cw` to run all Company website spiders with 5 spiders in parallel
"""

import getopt
import inspect
import multiprocessing as mp
import os
import queue
import subprocess
import sys

import scraping.emailer as emailer
import scraping.support.log_helper as lg
from scraping.base_spider import BaseSpider

import scraping.company_website.spiders as cw_spiders
from scraping.job_board.careerjet import CareerjetJb

SEP = '*' * 50
SEPNL = SEP + '\n'
NLSEP = '\n' + SEP
NLSEPNL = '\n' + SEP + '\n'


def print_help():
    lg.deflog.info('''HELP

Run as:

    python run.py [options] args

Options:
 -s / --super-parallel <S> run the super parallel mode (S spiders in parallel)
 -e / --email              run emailer after scraping
    ''')


def _run_in_parallel(spiders, retry_count, parellelism):
    # This is a way to run spiders truly in parallel
    # It's a bit of a hack - this script is simply called several times with by invoking a new Python process

    popens = []

    this_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(this_dir)

    popens.extend([['python', 'run.py', spider.name] for spider in spiders])

    popens = [popen[:-1] + ['-l', lg.get_file_name()] + popen[-1:] for popen in popens]

    if retry_count is not None:
        popens = [popen[:-1] + ['-r', str(retry_count)] + popen[-1:] for popen in popens]

    popen_queue = mp.Queue()
    for popen in popens:
        popen_queue.put(popen)

    def _worker(i, popen_queue):
        while True:
            try:
                popen = popen_queue.get(timeout=5)
            except queue.Empty:
                lg.deflog.info('{}Worker {} DONE{}'.format(NLSEPNL, i, NLSEP))
                return

            lg.deflog.info('{}Worker {} starting {}{}'.format(NLSEPNL, i, popen[-1], NLSEP))

            proc = subprocess.Popen(popen)
            try:
                proc.wait(24 * 3600)  # maximum running time - day
            except subprocess.TimeoutExpired as e:
                lg.deflog.info('Worker {} exception for {}: {}'.format(i, popen[-1], e))

    processes = [mp.Process(target=_worker, args=[i, popen_queue]) for i in range(parellelism)]
    for p in processes:
        p.start()

    for p in processes:
        p.join()


def run(spider_names, parellelism, retry_count, email):
    # here we build the list of spiders classes that we want to run
    spiders = []

    jbs = [CareerjetJb]
    jbs = [jb for jb in jbs if jb.name in spider_names]
    spiders.extend(jbs)

    # company website spiders
    cws = [i[1] for i in inspect.getmembers(cw_spiders, inspect.isclass) if
           str(i[0]).endswith('Spider') and str(i[0]) != 'BaseCwSpider']
    cws = [cw for cw in cws if cw.name in spider_names or 'cw' in spider_names]
    spiders.extend(cws)


    # now let's run those spiders!
    if parellelism is not None:
        _run_in_parallel(spiders, retry_count, parellelism)
    else:
        for spider in spiders:
            settings = spider.get_settings()
            if retry_count is None:
                spider.setup_for_multiple_exec(settings)
            else:
                spider.run_with_retry(settings, retry_count)

        BaseSpider.start_multiple_execution()

    if email:
        lg.deflog.info(SEP)
        lg.deflog.info('Going to send an email')
        lg.deflog.info('')
        emailer.emailer()

    lg.deflog.info('DONE')


def main():
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, 'hs:er:l:', ['help', 'super-parallel=', 'email', 'retry=', 'log='])
    except getopt.GetoptError:
        print('Wrong options')
        sys.exit()

    spider_names_to_run = args
    parellelism = None
    email = False
    retry_count = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_help()
            sys.exit()
        elif opt in ('-s', '--super-parallel'):
            parellelism = int(arg)
        elif opt in ('-e', '--email'):
            email = True
        elif opt in ('-r', '--retry'):
            retry_count = int(arg)
        elif opt in ('-l', '--log'):
            lg.set_file_name(arg)
        else:
            print('Wrong options')
            sys.exit()

    run(spider_names_to_run, parellelism, retry_count, email)


if __name__ == '__main__':
    main()
