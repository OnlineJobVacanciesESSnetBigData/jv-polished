"""Helper methods for selenium"""

import selenium.webdriver as wd
import scraping.support.general_helper as general_helper
from scraping.support.common import *
import selenium as se
import time


DEF_WAIT = 20


def get_driver():
    # this is here cause if many spiders request a driver, it demands lots of memory. So it can error out
    # the solution here is not ideal - ideally there would be a pool of drivers wrapped in Disposable object.
    # But so far I was lazy and this works!
    while True:
        try:
            options = se.webdriver.ChromeOptions()
            options.headless = True

            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ssl-protocol=any')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument("--test-type")

            capabilities = se.webdriver.DesiredCapabilities().CHROME
            capabilities['acceptSslCerts'] = True

            driver = wd.Chrome(desired_capabilities=capabilities, chrome_options=options)
            break
        except OSError:
            time.sleep(20)

    driver.set_page_load_timeout(120)
    driver.set_window_size(1200, 800)
    driver.set_window_position(-10000, 0)

    return driver


def screenshot(driver, logger):
    """Saves a screenshot from the current driver"""
    screenshot_path = from_root('log/screenshots/{}_{}.png'.format(
        general_helper.get_date(),
        general_helper.get_time()
    ), create_if_needed=True)

    logger.error('Saving screenshot for url {} to {}'.format(driver.current_url, screenshot_path))
    driver.save_screenshot(screenshot_path)


if __name__ == '__main__':
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options, executable_path=r'/usr/bin/chromedriver')
    driver.get("http://google.com/")
    print("Headless Chrome Initialized")
    driver.quit()

