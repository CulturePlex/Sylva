from selenium.common.exceptions import ElementNotVisibleException
from time import sleep


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
