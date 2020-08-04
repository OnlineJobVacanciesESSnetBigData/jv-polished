"""
Base spider class for company website spiders. This essentially extracts the code that would otherwise be the same
for each company website spider, and thus  makes it possible for the developer to focus only on specificities of
each company website when building a new spider.
"""

import functools
import traceback
import scrapy

import scraping.support.general_helper as general_helper
from scraping.base_spider import BaseSpider


class BaseCwSpider(BaseSpider):
    def __init__(self, err_queue=None):
        super().__init__(err_queue=err_queue)

        self._total = 0
        self._err_msg = None

    @property
    def urls_info(self):
        """
        Override this with method returning a list of dictionaries, each of which having two entries:
        - 'url': the url being scraped
        - 'extraction': the extraction applied (subclassing the class Extraction)

        Additional optional entry is 'pagination', specifying how to navigate pagination on the page

        See spiders.py for some examples
        """
        raise NotImplementedError

    @property
    def company_name(self):
        """Override this with method returning a string - the name of the company being scraped"""
        raise NotImplementedError

    def _spider_closed(self):
        if self._err_msg is None:
            self._logger.info('{} vacancies: "{}"'.format(self._total, self.company_name))
        else:
            self._logger.info('N/A vacancies: "{}"'.format(self.company_name))

    def _log_err(self, err_msg):
        self._err_msg = err_msg
        super()._log_err(err_msg)

    def start_requests(self):
        for url_info in self.urls_info:
            if 'pagination' in url_info:
                pagination = url_info['pagination']
                pagination.assign_logger(self._logger)
            else:
                pagination = None

            extraction = url_info['extraction']
            extraction.assign_logger(self._logger)

            callback = functools.partial(self._parse, extraction=extraction, pagination=pagination)
            try:
                yield scrapy.Request(url=url_info['url'], callback=callback, errback=self._errback, dont_filter=True)
            except Exception as e:
                self._log_err('Error making request: {}'.format(e))

    def _errback(self, failure):
        self._log_err('Request ended up in error: {}'.format(failure))

    def _parse(self, response, extraction, pagination):
        self._logger.debug("Scraping: {}".format(response.url))

        try:
            self._total += extraction.get_count(response)
        except Exception as e:
            self._log_err('Error getting count from {}: {}'.format(response.url, e))
            traceback.print_exc()

        try:
            if pagination is not None:
                self._logger.debug("Scraped count so far: {}".format(self._total))
                callback = functools.partial(self._parse, extraction=extraction, pagination=pagination)
                yield from pagination.next_url(response, extraction, callback)
        except Exception as e:
            self._log_err('Error paginating from {}: {}'.format(response.url, e))
            traceback.print_exc()
        finally:
            extraction.dispose()

    def _store_results(self):
        if self._err_msg is not None:
            self._total = None

        # TODO - here you can store the scraped data instead of just printing
        print(f'Company: {self.company_name}')
        print(f'Date: {general_helper.get_date()}')
        print(f'JV count: {self._total}')
        print(f'Error message: {self._err_msg}')

    @classmethod
    def get_settings(cls):
        settings = super().get_settings()
        settings.update({
            'COOKIES_ENABLED': True,
            'COOKIES_DEBUG': True
        })

        return settings
