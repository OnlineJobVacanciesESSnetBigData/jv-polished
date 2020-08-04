"""
Example of a job board spider - for Careerjet. https://www.careerjet.co.uk/

Simply run this file to try it out!
"""

import re
import string

import bs4 as bs
import scraping.job_board.items as items
import scrapy

from scraping.job_board.base_jb_spider import BaseJbSpider


class CareerjetJb(BaseJbSpider):
    """
    Spider scraping all job vacancy counts from Careerjet.
    """

    name = "careerjet"

    def __init__(self, err_queue=None):
        super().__init__(err_queue=err_queue)

        self.letters = self.__get_letters()
        self.urls = self.__get_urls()

    def __get_letters(self):
        """
        One for each on https://www.careerjet.co.uk/jobs/a.html
        """

        letters = ['1'] + [c for c in string.ascii_lowercase[:26]]
        return letters

    def __get_urls(self):
        return ['http://www.careerjet.co.uk/jobs/{LETTER}.html'.replace('{LETTER}', l) for l in self.letters]

    def start_requests(self):
        self._logger.info('Scraping from {} start urls'.format(self.name, len(self.urls)))

        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse_letter_page)

    def __extract_company_name(self, td):
        try:
            return td.find('a').attrs['title']
        except Exception as e:
            return 'EXTRACT_NAME_ERR ({})'.format(e)

    def __extract_link(self, td):
        try:
            return 'http://www.careerjet.co.uk' + td.find('a').attrs['href']
        except Exception as e:
            return 'EXTRACT_LINK_ERR ({})'.format(e)

    def __extract_count(self, td):
        try:
            count = re.search('\d+', list(td.children)[2])
            return int(count.group(0))
        except Exception as e:
            return 'EXTRACT_COUNT_ERR ({})'.format(e)

    def __extract_company_data(self, td):
        return items.CareerjetItem(
            company_name=self.__extract_company_name(td),
            link_internal=self.__extract_link(td),
            count=self.__extract_count(td)
        )

    def parse_letter_page(self, response):
        """
        Parsing the response using Beautiful Soup
        """
        letter = re.search('jobs/(.).html', response.url).group(1)

        soup = bs.BeautifulSoup(response.body, 'lxml')
        table = soup.find('div', {'id': 'heart'}).table
        tds = table.find_all('td')

        letter_data = list(map(self.__extract_company_data, tds))

        self._logger.info('Got data for {} companies for letter {}'.format(len(letter_data), letter))

        yield from letter_data

    @classmethod
    def get_jb_settings(cls):
        settings = super().get_jb_settings()
        settings.update({
            'FEED_EXPORT_FIELDS': ['company_name', 'link_internal', 'count'],
        })

        return settings


if __name__ == '__main__':
    CareerjetJb.run_single(CareerjetJb.get_jb_settings())
