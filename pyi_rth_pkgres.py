# uncompyle6 version 3.9.1
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 2.7.18 (default, Apr 18 2024, 23:37:34) 
# [GCC 13.2.0]
# Embedded file name: PyInstaller/loader/rthooks/pyi_rth_pkgres.py
import pkg_resources as res
from pyimod03_importers import FrozenImporter
res.register_loader_type(FrozenImporter, res.NullProvider)
