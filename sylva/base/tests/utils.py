from time import sleep


def spin_assert(assertion):
    for i in xrange(60):
        try:
            assertion()
            return
        except AssertionError as e:
            import ipdb
            ipdb.set_trace()
            pass
            sleep(1)
    raise e
