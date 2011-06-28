# -*- coding: utf-8 -*-

class BaseGraphDatabase(object):

    def __init__(self, url):
        self.url = url
