# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe  # noqa: ignore=F401

excludes = [
    "pywin",
    "pywin.debugger",
    "pywin.debugger.dbgcon",
    "pywin.dialogs",
    "pywin.dialogs.list",
    "win32com.server",
]

includes = [
    # files to include
]

options = {
    'bundle_files': 1,  # create singlefile exe
    'compressed': 1,  # compress the library archive
    'optimize': 2,
    'excludes': excludes,
    'includes': includes,
    'dll_excludes': ['w9xpopen.exe'],  # we don't need this
    'dist_dir': './dist'
}

setup(
    # information
    name="CCleaner Auto Updater",
    version="0.5",
    description="CCleaner Automatic Updater",
    author="Bumsoo Kim",
    author_email="bskim45@gmail.com",
    url="https://bsk.im",

    # packaging
    options={"py2exe": options},
    zipfile=None,  # append zip-archive to the executable

    console=['CCleanerAutoUpdate.py']
)
