"""
Module with the base class for job-board spiders, i.e. spiders scraping job vacancy counts from job boards.
"""

import pandas as pd
import scraping.support.general_helper as general_helper
from scraping.base_spider import BaseSpider
from scraping.support.common import *


class BaseJbSpider(BaseSpider):
    """
    Base class for a job-board spiders. See Careerjet spider for example of usage
    """
    def __init__(self, err_queue=None):
        super().__init__(err_queue)

    def _store_results(self):
        feed_uri = self.settings['FEED_URI']
        df = pd.read_csv(feed_uri)
        entries = df.to_dict(orient='records')

        print('Scraped results:')
        print(entries)
        # TODO here you can store the data, e.g. in Mongo database

    def _try_extract(self, extraction_method, *args, **kwargs):
        try:
            return extraction_method(*args, **kwargs)
        except Exception as e:
            self._logger.error('Error extracting applying {} on {}: {}'.format(extraction_method.__name__, args, e))
            return None

    @classmethod
    def get_jb_settings(cls):
        # this feed Scrapy setting will cause the spider to save all scraped data in a CSV file
        # at the path spec. by feed_uri. In other words, the scraped data will be stored in a CSV file
        # so that when the spider is closing, one can e.g. print the results, or store them in Mongo DB etc...

        output_path = 'scraped/job_board/{}_{}.csv'.format(cls.name, general_helper.get_date())
        feed_uri = from_data_root(output_path, create_if_needed=True)
        if os.path.exists(feed_uri):
            os.remove(feed_uri)

        settings = BaseSpider.get_settings()
        settings.update({
            'FEED_URI': feed_uri,
            'FEED_FORMAT': 'csv',
            'CONCURRENT_REQUESTS': 1,
            'DOWNLOAD_DELAY': 3
        })

        return settings