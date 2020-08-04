"""
Helper methods/classes to faciliate extraction of the required data from the HTML
"""


import scraping.support.selenium_helper as sel_helper
import re
from selenium.webdriver.support.ui import WebDriverWait
import scraping.support.selenium_helper as sh


# ---------------------------------------------------------------------
# --- Extraction types
# ---------------------------------------------------------------------

class Extraction:
    """Subclass this to describe extraction from a HTTP response"""
    def assign_logger(self, logger):
        self._logger = logger

    def get_count_from_response(self, response):
        """Override with code extracting the desired integer from the HTTP response"""
        raise NotImplementedError

    def get_count(self, response):
        count = self.get_count_from_response(response)
        if not isinstance(count, int):
            raise Exception('Value must be converted to integer class: {}'.format(count))
        else:
            return count

    def dispose(self):
        pass


class SeleniumExtraction(Extraction):
    """Subclass this to describe extraction from a Selenium driver"""
    DEF_WAIT = 30

    def __init__(self):
        self.driver = None

    def get_count_via_driver(self, driver, response):
        """Override with code extracting the desired number from the Selenium driver, or the HTTP response"""
        raise NotImplementedError

    def get_count_from_response(self, response):
        if self.driver is not None:
            self.driver.quit()

        self.driver = sel_helper.get_driver()

        try:
            self.driver.get(response.url)
        except Exception as e:
            self._logger.error('Error loading page: ' + str(e))
            raise e

        try:
            return self.get_count_via_driver(self.driver, response)
        except Exception as e:
            self._logger.error('Error getting counts using web-driver: ' + str(e))
            sel_helper.screenshot(self.driver, self._logger)

            raise e

    def dispose(self):
        self.driver.quit()


# ---------------------------------------------------------------------
# --- Helper methods to take care of common scenarios
# ---------------------------------------------------------------------


def simple_xpath_regex_extraction(xpath, pattern='(\d+)'):
    """For cases where we just take a number representing the count directly"""
    class NewExtraction(Extraction):
        def get_count_from_response(self, response):
            text = response.xpath(xpath).extract_first()
            return int(re.search(pattern, text).group(1))

    return NewExtraction()


def simple_xpath_count_extraction(xpath):
    """For cases where we just count number of job ads given by specified xpath"""
    class NewExtraction(Extraction):
        def get_count_from_response(self, response):
            return len(response.xpath(xpath).extract())

    return NewExtraction()


def wait_for_element(driver, expectation):
    element = WebDriverWait(driver, sh.DEF_WAIT).until(expectation)

    return element
