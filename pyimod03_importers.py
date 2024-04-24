# uncompyle6 version 3.9.1
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 2.7.18 (default, Apr 18 2024, 23:37:34) 
# [GCC 13.2.0]
# Embedded file name: /usr/local/lib/python2.7/dist-packages/PyInstaller/loader/pyimod03_importers.py
# Compiled at: 2016-05-03 15:32:20
"""
PEP-302 importers for frozen applications.
"""
import sys, pyimod01_os_path as pyi_os_path
from pyimod02_archive import ArchiveReadError, ZlibArchiveReader
SYS_PREFIX = sys._MEIPASS
SYS_PREFIXLEN = len(SYS_PREFIX)
if sys.version_info[0:2] < (3, 3):
    import imp
    imp_lock = imp.acquire_lock
    imp_unlock = imp.release_lock
    EXTENSION_SUFFIXES = dict((f[0], f) for f in imp.get_suffixes() if f[2] == imp.C_EXTENSION)
    imp_new_module = imp.new_module
else:

    def imp_lock():
        pass


    def imp_unlock():
        pass


    import _frozen_importlib
    if sys.version_info[1] <= 4:
        EXTENSION_SUFFIXES = _frozen_importlib.EXTENSION_SUFFIXES
        EXTENSION_LOADER = _frozen_importlib.ExtensionFileLoader
    else:
        EXTENSION_SUFFIXES = _frozen_importlib._bootstrap_external.EXTENSION_SUFFIXES
        EXTENSION_LOADER = _frozen_importlib._bootstrap_external.ExtensionFileLoader
    imp_new_module = type(sys)
if sys.flags.verbose:

    def trace(msg, *a):
        sys.stderr.write(msg % a)
        sys.stderr.write('\n')


else:

    def trace(msg, *a):
        pass


class BuiltinImporter(object):
    """
    PEP-302 wrapper of the built-in modules for sys.meta_path.

    This wrapper ensures that import machinery will not look for built-in
    modules in the bundled ZIP archive.
    """

    def find_module(self, fullname, path=None):
        imp_lock()
        module_loader = None
        if fullname in sys.builtin_module_names:
            module_loader = self
        imp_unlock()
        return module_loader

    def load_module(self, fullname, path=None):
        imp_lock()
        try:
            try:
                module = sys.modules.get(fullname)
                if module is None:
                    module = imp.init_builtin(fullname)
            except Exception:
                if fullname in sys.modules:
                    sys.modules.pop(fullname)
                raise

        finally:
            imp_unlock()

        return module

    def is_package(self, fullname):
        """
        Return always False since built-in modules are never packages.
        """
        if fullname in sys.builtin_module_names:
            return False
        raise ImportError('No module named ' + fullname)

    def get_code(self, fullname):
        """
        Return None for a built-in module.
        """
        if fullname in sys.builtin_module_names:
            return
        else:
            raise ImportError('No module named ' + fullname)
            return

    def get_source(self, fullname):
        """
        Return None for a built-in module.
        """
        if fullname in sys.builtin_module_names:
            return
        else:
            raise ImportError('No module named ' + fullname)
            return


class FrozenPackageImporter(object):
    """
    Wrapper class for FrozenImporter that imports one specific fullname from
    a module named by an alternate fullname. The alternate fullname is derived from the
    __path__ of the package module containing that module.

    This is called by FrozenImporter.find_module whenever a module is found as a result
    of searching module.__path__
    """

    def __init__(self, importer, fullname):
        self._fullname = fullname
        self._importer = importer

    def load_module(self, fullname):
        return self._importer.load_module(fullname, self._fullname)


class FrozenImporter(object):
    """
    Load bytecode of Python modules from the executable created by PyInstaller.

    Python bytecode is zipped and appended to the executable.

    NOTE: PYZ format cannot be replaced by zipimport module.

    The problem is that we have no control over zipimport; for instance,
    it doesn't work if the zip file is embedded into a PKG appended
    to an executable, like we create in one-file.

    This is PEP-302 finder and loader class for the ``sys.meta_path`` hook.
    A PEP-302 finder requires method find_module() to return loader
    class with method load_module(). Both these methods are implemented
    in one class.

    To use this class just call

        FrozenImporter.install()
    """

    def __init__(self):
        """
        Load, unzip and initialize the Zip archive bundled with the executable.
        """
        for pyz_filepath in sys.path:
            imp_lock()
            try:
                try:
                    self._pyz_archive = ZlibArchiveReader(pyz_filepath)
                    sys.path.remove(pyz_filepath)
                    self.toc = set(self._pyz_archive.toc.keys())
                    trace('# PyInstaller: FrozenImporter(%s)', pyz_filepath)
                    return
                except IOError:
                    continue
                except ArchiveReadError:
                    continue

            finally:
                imp_unlock()

        raise ImportError("Can't load frozen modules.")

    def __call__(self, path):
        """
        PEP-302 sys.path_hook processor.

        sys.path_hook is a list of callables, which will be checked in
        sequence to determine if they can handle a given path item.
        """
        if path.startswith(SYS_PREFIX):
            fullname = path[SYS_PREFIXLEN + 1:].replace(pyi_os_path.os_sep, '.')
            loader = self.find_module(fullname)
            if loader is not None:
                return loader
        raise ImportError(path)
        return

    def find_module(self, fullname, path=None):
        """
        PEP-302 finder.find_module() method for the ``sys.meta_path`` hook.

        fullname     fully qualified name of the module
        path         None for a top-level module, or package.__path__ for submodules or subpackages.

        Return a loader object if the module was found, or None if it wasn't. If find_module() raises
        an exception, it will be propagated to the caller, aborting the import.
        """
        imp_lock()
        module_loader = None
        if fullname in self.toc:
            module_loader = self
            trace('import %s # PyInstaller PYZ', fullname)
        elif path is not None:
            modname = fullname.split('.')[-1]
            for p in path:
                p = p.replace(SYS_PREFIX, '')
                parts = p.split(pyi_os_path.os_sep)
                if not len(parts):
                    continue
                if not parts[0]:
                    parts = parts[1:]
                parts.append(modname)
                real_fullname = ('.').join(parts)
                if real_fullname in self.toc:
                    module_loader = FrozenPackageImporter(self, real_fullname)
                    trace('import %s as %s # PyInstaller PYZ (__path__ override: %s)', real_fullname, fullname, p)
                    break

        imp_unlock()
        if module_loader is None:
            trace('# %s not found in PYZ', fullname)
        return module_loader

    def load_module(self, fullname, real_fullname=None):
        """
        PEP-302 loader.load_module() method for the ``sys.meta_path`` hook.

        Return the loaded module (instance of imp_new_module()) or raises
        an exception, preferably ImportError if an existing exception
        is not being propagated.

        When called from FrozenPackageImporter, `real_fullname` is the name of the
        module as it is stored in the archive. This module will be loaded and installed
        into sys.modules using `fullname` as its name
        """
        imp_lock()
        module = None
        if real_fullname is None:
            real_fullname = fullname
        try:
            try:
                module = sys.modules.get(fullname)
                if module is None:
                    is_pkg, bytecode = self._pyz_archive.extract(real_fullname)
                    module = imp_new_module(fullname)
                    if is_pkg:
                        module.__file__ = pyi_os_path.os_path_join(pyi_os_path.os_path_join(SYS_PREFIX, fullname.replace('.', pyi_os_path.os_sep)), '__init__.pyc')
                    else:
                        module.__file__ = pyi_os_path.os_path_join(SYS_PREFIX, fullname.replace('.', pyi_os_path.os_sep) + '.pyc')
                    if is_pkg:
                        module.__path__ = [
                         pyi_os_path.os_path_dirname(module.__file__)]
                    module.__loader__ = self
                    if is_pkg:
                        module.__package__ = fullname
                    else:
                        module.__package__ = fullname.rsplit('.', 1)[0]
                    if sys.version_info[0:2] > (3, 3):
                        module.__spec__ = _frozen_importlib.ModuleSpec(real_fullname, self, is_package=is_pkg)
                    sys.modules[fullname] = module
                    exec(bytecode, module.__dict__)
                    module = sys.modules[fullname]
            except Exception:
                if fullname in sys.modules:
                    sys.modules.pop(fullname)
                raise

        finally:
            imp_unlock()

        return module

    def is_package(self, fullname):
        """
        Return always False since built-in modules are never packages.
        """
        if fullname in self.toc:
            try:
                is_pkg, bytecode = self._pyz_archive.extract(fullname)
                return bool(is_pkg)
            except Exception:
                raise ImportError('Loader FrozenImporter cannot handle module ' + fullname)

        else:
            raise ImportError('Loader FrozenImporter cannot handle module ' + fullname)

    def get_code(self, fullname):
        """
        Get the code object associated with the module.

        ImportError should be raised if module not found.
        """
        if fullname in self.toc:
            try:
                is_pkg, bytecode = self._pyz_archive.extract(fullname)
                return bytecode
            except Exception:
                raise ImportError('Loader FrozenImporter cannot handle module ' + fullname)

        else:
            raise ImportError('Loader FrozenImporter cannot handle module ' + fullname)

    def get_source(self, fullname):
        """
        Method should return the source code for the module as a string.
        But frozen modules does not contain source code.

        Return None.
        """
        if fullname in self.toc:
            return
        else:
            raise ImportError('No module named ' + fullname)
            return

    def get_data(self, path):
        """
        This returns the data as a string, or raise IOError if the "file"
        wasn't found. The data is always returned as if "binary" mode was used.

        This method is useful getting resources with 'pkg_resources' that are
        bundled with Python modules in the PYZ archive.

        The 'path' argument is a path that can be constructed by munging
        module.__file__ (or pkg.__path__ items)
        """
        assert path.startswith(SYS_PREFIX + pyi_os_path.os_sep)
        fullname = path[len(SYS_PREFIX) + 1:]
        if fullname in self.toc:
            return self._pyz_archive.extract(fullname)[1]
        with open(path, 'rb') as fp:
            return fp.read()

    def get_filename(self, fullname):
        """
        This method should return the value that __file__ would be set to
        if the named module was loaded. If the module is not found, then
        ImportError should be raised.
        """
        if self.is_package(fullname):
            filename = pyi_os_path.os_path_join(pyi_os_path.os_path_join(SYS_PREFIX, fullname.replace('.', pyi_os_path.os_sep)), '__init__.pyc')
        else:
            filename = pyi_os_path.os_path_join(SYS_PREFIX, fullname.replace('.', pyi_os_path.os_sep) + '.pyc')
        return filename


class CExtensionImporter(object):
    """
    PEP-302 hook for sys.meta_path to load Python C extension modules.

    C extension modules are present on the sys.prefix as filenames:

        full.module.name.pyd
        full.module.name.so
        full.module.name.cpython-33m.so
        full.module.name.abi3.so
    """

    def __init__(self):
        files = pyi_os_path.os_listdir(SYS_PREFIX)
        self._file_cache = set(files)

    def find_module(self, fullname, path=None):
        imp_lock()
        module_loader = None
        for ext in EXTENSION_SUFFIXES:
            if fullname + ext in self._file_cache:
                module_loader = self
                break

        imp_unlock()
        return module_loader

    def load_module(self, fullname, path=None):
        imp_lock()
        module = None
        try:
            try:
                if sys.version_info[0] == 2:
                    module = sys.modules.get(fullname)
                    if module is None:
                        for ext, ext_tuple in list(EXTENSION_SUFFIXES.items()):
                            filename = fullname + ext
                            if filename in self._file_cache:
                                break

                        filename = pyi_os_path.os_path_join(SYS_PREFIX, filename)
                        fp = open(filename, 'rb')
                        module = imp.load_module(fullname, fp, filename, ext_tuple)
                        if hasattr(module, '__setattr__'):
                            module.__file__ = filename
                        else:
                            module.__dict__['__file__'] = filename
                else:
                    module = sys.modules.get(fullname)
                    if module is None:
                        for ext in EXTENSION_SUFFIXES:
                            filename = pyi_os_path.os_path_join(SYS_PREFIX, fullname + ext)
                            try:
                                with open(filename):
                                    pass
                            except IOError:
                                continue

                            loader = EXTENSION_LOADER(fullname, filename)
                            module = loader.load_module(fullname)

            except Exception:
                if fullname in sys.modules:
                    sys.modules.pop(fullname)
                raise

        finally:
            imp_unlock()

        return module

    def is_package(self, fullname):
        """
        Return always False since C extension modules are never packages.
        """
        return False

    def get_code(self, fullname):
        """
        Return None for a C extension module.
        """
        for ext in EXTENSION_SUFFIXES:
            if fullname + ext in self._file_cache:
                return

        raise ImportError('No module named ' + fullname)
        return

    def get_source(self, fullname):
        """
        Return None for a C extension module.
        """
        return self.get_code(fullname)

    def get_data(self, path):
        """
        This returns the data as a string, or raise IOError if the "file"
        wasn't found. The data is always returned as if "binary" mode was used.

        The 'path' argument is a path that can be constructed by munging
        module.__file__ (or pkg.__path__ items)
        """
        fp = open(path, 'rb')
        content = fp.read()
        fp.close()
        return content

    def get_filename(self, fullname):
        """
        This method should return the value that __file__ would be set to
        if the named module was loaded. If the module is not found, then
        ImportError should be raised.
        """
        for ext in EXTENSION_SUFFIXES:
            if fullname + ext in self._file_cache:
                return pyi_os_path.os_path_join(SYS_PREFIX, fullname + ext)

        raise ImportError('No module named ' + fullname)


def install():
    """
    Install FrozenImporter class and other classes into the import machinery.

    This class method (static method) installs the FrozenImporter class into
    the import machinery of the running process. The importer is added
    to sys.meta_path. It could be added to sys.path_hooks but sys.meta_path
    is processed by Python before looking at sys.path!

    The order of processing import hooks in sys.meta_path:

    1. built-in modules
    2. modules from the bundled ZIP archive
    3. C extension modules
    4. Modules from sys.path
    """
    if sys.version_info[0] == 2:
        sys.meta_path.append(BuiltinImporter())
    fimp = FrozenImporter()
    sys.meta_path.append(fimp)
    sys.path_hooks.append(fimp)
    sys.meta_path.append(CExtensionImporter())
    if sys.version_info[0] > 2:
        for item in sys.meta_path:
            if hasattr(item, '__name__') and item.__name__ == 'WindowsRegistryFinder':
                sys.meta_path.remove(item)
                break

        pf_idx = 2
        pf = sys.meta_path.pop(pf_idx)
        sys.meta_path.append(pf)
