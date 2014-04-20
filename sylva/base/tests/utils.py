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
