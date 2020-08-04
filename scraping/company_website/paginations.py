"""
Helper class for handling pages which require use of pagination
"""

import scrapy


class Pagination:
    """Subclass this to describe pagination on the page"""
    def assign_logger(self, logger):
        self._logger = logger

    def get_next_url(self, response, extraction):
        """Override with code to get the next page url, or None if this is the last page"""
        raise NotImplementedError

    def next_url(self, response, extraction, callback):
        next_url = self.get_next_url(response, extraction)
        if next_url is not None:
            yield scrapy.Request(url=next_url, callback=callback)