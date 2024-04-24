# uncompyle6 version 3.9.1
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 2.7.18 (default, Apr 18 2024, 23:37:34) 
# [GCC 13.2.0]
# Embedded file name: /usr/local/lib/python2.7/dist-packages/PyInstaller/loader/pyimod01_os_path.py
# Compiled at: 2016-05-03 15:32:20
"""
Set up 'os' and 'os.path' module replacement functions for use during import
bootstrap.
"""
import sys
_builtin_names = sys.builtin_module_names
_mindirlen = 0
if 'posix' in _builtin_names:
    from posix import environ as os_environ
    from posix import listdir as os_listdir
    os_sep = '/'
    _mindirlen = 1
elif 'nt' in _builtin_names:
    from nt import environ as os_environ
    from nt import listdir as os_listdir
    os_sep = '\\'
    _mindirlen = 3
else:
    raise ImportError('No os specific module found')

def os_path_join(a, b, sep=os_sep):
    if a == '':
        return b
    lastchar = a[-1:]
    if lastchar == '/' or lastchar == sep:
        return a + b
    return a + sep + b


def os_path_dirname(a, sep=os_sep, mindirlen=_mindirlen):
    for i in range(len(a) - 1, -1, -1):
        c = a[i]
        if c == '/' or c == sep:
            if i < mindirlen:
                return a[:i + 1]
            return a[:i]

    return ''


if sys.platform.startswith('win'):

    def os_path_basename(pth):
        if pth[1:2] == ':':
            d = pth[0:2]
            p = pth[2:]
        else:
            d = ''
            p = pth
        i = len(p)
        while i and p[i - 1] not in '/\\':
            i = i - 1

        head, tail = p[:i], p[i:]
        return tail


else:

    def os_path_basename(pth):
        i = pth.rfind('/') + 1
        return pth[i:]


if 'PYTHONCASEOK' not in os_environ:

    def caseOk(filename):
        files = os_listdir(os_path_dirname(filename))
        return os_path_basename(filename) in files


else:

    def caseOk(filename):
        return True
