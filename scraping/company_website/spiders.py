"""
Examples of company-website spiders. Always one class per one spider (~ 1 company)

Simply run this file to try it out!
"""

from scraping.company_website.extractions import *
from scraping.company_website.paginations import *
from selenium.webdriver.common.by import By
from scraping.company_website.base_cw_spider import BaseCwSpider
import time
import selenium.webdriver.support.expected_conditions as ec


class AccentureUkLtdCwSpider(BaseCwSpider):
    """
    Example of extraction using Selenium, as content is loaded asynchronously

    This spider tends to have problems with SSL errors. Did not find a solution yet.
    """

    name = 'accenture-uk'

    @property
    def company_name(self):
        return 'ACCENTURE (UK) LIMITED INCL ACCENTURE SERVICES LTD & ACCENTURE SYSTEMS INTEGRATION LTD	'

    class Extraction(SeleniumExtraction):
        def get_count_via_driver(self, driver, response):
            element = wait_for_element(driver, ec.visibility_of_element_located((
                By.XPATH, '//span[@class="search-results-count total-jobs-count"]'
            )))  # we wait for the element to appear

            # the next one is somehow necessary so that the number shows in the previous element
            wait_for_element(driver, ec.visibility_of_element_located((
                By.XPATH, '//div[@class="job noPaddingTop noPaddingBottom"]'
            )))

            count = int(re.search('(\d+)', element.text).group(1))
            return count

    @property
    def urls_info(self):
        return [{
            'url': 'https://www.accenture.com/gb-en/careers/jobsearch',
            'extraction': self.Extraction()
        }]



class AecomCwSpider(BaseCwSpider):
    """Example of extraction where desired content is loaded directly with the page"""

    name = "aecom-cw"

    @property
    def company_name(self):
        return 'AECOM LTD INCL ALL VAT GROUP MEMBERS'

    @property
    def urls_info(self):
        return [{
            'url': 'http://aecom.jobs/gbr/jobs/',
            'extraction': simple_xpath_regex_extraction(
                xpath='//h3[contains(text(), " Jobs in United Kingdom")]/text()',
                pattern='(\d+) Jobs in United Kingdom'
            ),
        }]


class AonCwSpider(BaseCwSpider):
    """A more complicated example, with:
    - paginated list of job vacancies
    - asynchronous loading of the desired content
    - the content is in an iframe, to which we need to switch before locating the desired element
    - need to filter the job vacancies for those that are in the UK
    """

    name = "aon-cw"

    @property
    def company_name(self):
        return 'AON UK LTD INCL ALL VAT GROUP MEMBERS EXC HEWITT ASSOCIATES'

    class Extraction(SeleniumExtraction):
        def get_count_via_driver(self, driver, response):
            driver.switch_to.frame('icims_content_iframe')

            element = wait_for_element(driver, ec.presence_of_element_located((
                By.CLASS_NAME, 'iCIMS_JobsTable'
            )))
            rows = element.find_elements_by_class_name('row')
            in_uk = [r for r in rows if 'GB-' in r.text]

            return len(in_uk)

    class Pagination(Pagination):
        def get_next_url(self, response, extraction):
            paginator = extraction.driver.find_element_by_class_name('iCIMS_Paginator_Bottom')
            try:
                next_arrow = paginator.find_element_by_css_selector('a.glyph:nth-of-type(3)')
                return next_arrow.get_attribute('href')
            except:
                return None

    @property
    def urls_info(self):
        return [{
            'url': 'https://uk-aon.icims.com/jobs/search?pr=0',
            'extraction': self.Extraction(),
            'pagination': self.Pagination()
        }]


class HalfordsCwSpider(BaseCwSpider):
    """Example where we combine counts from more page/elements"""
    name = "halfords-cw"

    @property
    def reporting_unit(self):
        return 'HALFORDS LTD INCL HALFORDS HLDGS LTD HALFORDS GRP LTD HALFORDS FIN LTD HALFORDS HLDGS 2006 LTD'

    @property
    def urls_info(self):
        return [
            {
                'url': 'http://jobs.halfordscareers.com/cw/en/listing',
                'extraction': simple_xpath_count_extraction(xpath='//a[@class="job-link"]')
            },
            {
                'url': 'http://jobs.halfordscareers.com/cw/en/listing',
                'extraction': simple_xpath_regex_extraction(
                    xpath='//a[@class="more-link button"]/span[@class="count"]/text()',
                    pattern='(\d+)'
                )
            }
        ]



class BritishHeartCwSpider(BaseCwSpider):
    """Example with data being already on the page (no need for Selenium), but need for extracting them with
    bit more code"""

    name = 'british-heart-cw'

    @property
    def company_name(self):
        return 'BRITISH HEART FOUNDATION'

    class MyExtraction(Extraction):
        def get_count_from_response(self, response):
            xpath = "//div[contains(text(), 'Displaying')]"
            return int(re.search('Displaying 1-\d+ of (\d+)', response.xpath(xpath).extract()[0]).group(1))

    @property
    def urls_info(self):
        return [
            {
                'url': 'https://jobs.bhf.org.uk/vacancies/vacancy-search-results.aspx',
                'extraction': self.MyExtraction()
            }
        ]


class JacobsUkLtdCwSpider(BaseCwSpider):
    name = "jacobs-uk-ltd-cw"

    @property
    def company_name(self):
        return 'JACOBS UK LTD INCL JACOBS UK HOLD LTD&JACOBS PROCESS&JACOBS ONE&JACOBS E&C INTER&JACOBS E&C LTD'

    class Extraction(SeleniumExtraction):
        def get_count_via_driver(self, driver, response):
            time.sleep(5)
            wait_for_element(driver, ec.visibility_of_element_located((
                By.XPATH, '(//input[@role="textbox"])[2]'
            ))).send_keys('United Kingdom')

            time.sleep(5)
            wait_for_element(driver, ec.presence_of_element_located((
                By.XPATH, '//input[@id="search"]'
            ))).click()

            time.sleep(5)
            element = wait_for_element(driver, ec.presence_of_element_located((
                By.XPATH, '//span[@id="currentPageInfo"]'
            )))

            return int(re.search(' of (\d+)', element.text).group(1))

    @property
    def urls_info(self):
        return [{
            'url': 'https://jacobs.taleo.net/careersection/ex/jobsearch.ftl?lang=en',
            'extraction': self.Extraction()
        }]




if __name__ == '__main__':
    AccentureUkLtdCwSpider.setup_for_multiple_exec(AccentureUkLtdCwSpider.get_settings())
    AecomCwSpider.setup_for_multiple_exec(AecomCwSpider.get_settings())
    AonCwSpider.setup_for_multiple_exec(AonCwSpider.get_settings())
    HalfordsCwSpider.setup_for_multiple_exec(HalfordsCwSpider.get_settings())
    BritishHeartCwSpider.setup_for_multiple_exec(BritishHeartCwSpider.get_settings())
    JacobsUkLtdCwSpider.setup_for_multiple_exec(JacobsUkLtdCwSpider.get_settings())
    BaseCwSpider.start_multiple_execution()
