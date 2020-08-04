"""
Base class for all spiders. This mainly extracts common code across the spiders, set's up hooks for important points
of the spider's lifetime (e.g. when spider is being closed, we might want to store data it scraped) and prints
log messages.
"""

import time
import scrapy
import scrapy.signals as signals
from multiprocessing import Process, Queue
import scraping.support.log_helper as lg
import scrapy.crawler as crawler
import twisted.internet.reactor as reactor


class BaseSpider(scrapy.Spider):
    def __init__(self, err_queue=None):
        super().__init__()

        self._err_queue = err_queue if err_queue is not None else Queue()

        self._logger = lg.get_logger(self.name)

    def _log_err(self, err_msg):
        """
        Use this method to log an error - other than printing the error, it is also stored in the error queue, which
        is e.g. monitored when running the spider using the "retry on error" mode (see function below)
        """
        err = Exception('Exception occured in {}: {}'.format(self.name, err_msg))
        self._err_queue.put(err)
        self._logger.error(err_msg)

    def __spider_error(self, failure, response):
        err_msg = "Error on {0}, traceback: {1}".format(response.url, failure.getTraceback())
        self._log_err(err_msg)

    def __spider_opened(self):
        self._start_time = time.time()
        self._logger.info('Starting {}'.format(self.name))

    def _spider_closed(self):
        pass

    def __spider_closed(self):
        self._spider_closed()

        self._store_results()

        self._logger.info('Finished {0}. Execution took: {1:.2f}s'.format(self.name, time.time() - self._start_time))

    def _store_results(self):
        """Override to store results at this point"""
        raise NotImplementedError

    def __store_results(self):
        try:
            self._logger.info('Storing results...')
            t = time.time()

            self._store_results()

            self._logger.info('Results stored. Took: {0:.2f}s'.format(time.time() - t))
        except Exception as e:
            self._log_err('Error storing data in Mongo: {}'.format(e))
            import traceback
            traceback.print_exc()

    @classmethod
    def get_settings(cls):
        return {
            'USER_AGENT': 'my_test_spider',
            'LOG_ENABLED': False,
            'BOT_NAME': 'my_test_bot',
            'ROBOTSTXT_OBEY': True
        }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)

        crawler.signals.connect(spider.__spider_error, signal=signals.spider_error)
        crawler.signals.connect(spider.__spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.__spider_closed, signal=signals.spider_closed)

        return spider

    # ---------------------------------------------------------------------
    # --- Parallel execution
    # ---------------------------------------------------------------------

    _multiple_mode_runners = []

    @classmethod
    def setup_for_multiple_exec(cls, settings, *init_args, **init_kwargs):
        """
        Use this when you want to execute more spiders. This will only setup an execution of the spider,
        but will not actually start it. The execution must be explicitly triggered with start_execution
        """
        runner = crawler.CrawlerRunner(settings)
        cls._multiple_mode_runners.append(runner)
        deferred = runner.crawl(cls, *init_args, **init_kwargs)

        def _spider_finished(runner):
            cls._multiple_mode_runners.remove(runner)
            if len(cls._multiple_mode_runners) == 0:
                reactor.stop()

        deferred.addBoth(lambda _: _spider_finished(runner))

    @classmethod
    def start_multiple_execution(cls):
        """
        Triggers the execution of spiders that were set up
        """
        if len(cls._multiple_mode_runners) > 0:
            reactor.run()

    @classmethod
    def run_single(cls, settings, *init_args, **init_kwargs):
        """
        Runs just a single spider
        """
        cls.setup_for_multiple_exec(settings, *init_args, **init_kwargs)
        cls.start_multiple_execution()


    # ---------------------------------------------------------------------
    # --- Run with retry
    # ---------------------------------------------------------------------

    @classmethod
    def run_with_retry(cls, settings, trials=2, *init_args, **init_kwargs):
        """
        This method can be used to re-run spider in case there was an error in the execution.

        :param trials: how many times to retry at most
        """
        trials -= 1

        try:
            cls.__run_in_separate_process(settings, *init_args, **init_kwargs)
        except:
            if trials == 0:
                raise

            print(f'Retrying. Remaining trials = {trials}')

            cls.run_with_retry(settings, trials=trials, *init_args, **init_kwargs)

    @classmethod
    def __run_in_separate_process(cls, settings, *init_args, **init_kwargs):
        """
        This method runs the spider in a separate process and monitors the error queue. If there was an error, it
        will be fetched from the queue and raised.

        Running spider in a separate process is necessary because Scrapy uses "reactor" which is not restartable.

        See https://stackoverflow.com/questions/41495052/scrapy-reactor-not-restartable
        """
        def _process_method(err_queue):
            try:
                runner = crawler.CrawlerRunner(settings)
                deferred = runner.crawl(cls, *init_args, **init_kwargs, err_queue=err_queue)

                def _cb():
                    err_queue.put(None)
                    reactor.stop()

                deferred.addBoth(lambda _: _cb())

                reactor.run()
            except Exception as e:
                err_queue.put(e)

        queue = Queue()
        process = Process(target=_process_method, args=(queue,))
        process.start()

        errs = []
        err = queue.get()
        while err is not None:
            errs.append(err)
            err = queue.get()
        process.join()

        if len(errs) > 0:
            raise errs[0]