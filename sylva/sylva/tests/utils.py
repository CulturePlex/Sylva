from selenium.common.exceptions import ElementNotVisibleException
from time import sleep

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from splinter import Browser as SplinterBrowser
from splinter.driver.webdriver import BaseWebDriver, WebDriverElement
from splinter.driver.webdriver.cookie_manager import CookieManager


class WebDriver(BaseWebDriver):

    driver_name = "firefox"

    def __init__(self, profile=None, extensions=None, user_agent=None,
                 profile_preferences=None, wait_time=2, firefox_path=None):
        firefox_profile = FirefoxProfile(profile)
        firefox_profile.set_preference('extensions.logging.enabled', False)
        firefox_profile.set_preference('network.dns.disableIPv6', False)
        if user_agent is not None:
            firefox_profile.set_preference('general.useragent.override',
                                           user_agent)
        if profile_preferences:
            for key, value in profile_preferences.items():
                firefox_profile.set_preference(key, value)
        if extensions:
            for extension in extensions:
                firefox_profile.add_extension(extension)
        if firefox_path:
            firefox_binary = FirefoxBinary(firefox_path=firefox_path)
            self.driver = Firefox(firefox_profile=firefox_profile,
                                  firefox_binary=firefox_binary)
        else:
            self.driver = Firefox(firefox_profile)
        self.element_class = WebDriverElement
        self._cookie_manager = CookieManager(self.driver)
        super(WebDriver, self).__init__(wait_time)


def Browser(driver_name='firefox', *args, **kwargs):
    if driver_name == 'firefox' and kwargs.get('firefox_path') is not None:
        return WebDriver(*args, **kwargs)
    else:
        return SplinterBrowser(driver_name, *args, **kwargs)


def spin_assert(assertion):
    for i in xrange(60):
        try:
            assertion()
            return
        except AssertionError as e:
            pass
            sleep(1)
    raise e


def spin_click(element_1, element_2):
    for i in xrange(60):
        try:
            element_1.click()
            element_2.click()
            return
        except ElementNotVisibleException as e:
            pass
            sleep(1)
    raise e
