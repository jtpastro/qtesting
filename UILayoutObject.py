# uncompyle6 version 3.9.1
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 2.7.18 (default, Apr 18 2024, 23:37:34) 
# [GCC 13.2.0]
# Embedded file name: event_extractor/UILayoutObject.py


class UILayoutObject:

    def __init__(self, cis, pkg_name, class_name):
        self.cis = cis
        self.pkg_name = pkg_name
        self.class_name = class_name
        self.isListView = False

    def setIsListView(self, isListView):
        self.isListView = isListView
