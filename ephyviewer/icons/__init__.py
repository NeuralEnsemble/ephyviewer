import sys


if sys.version_info > (3,):
    # py3x Qt5
    from . import  icons_py3 as icons
else:
    # py27 Qt4
    from . import  icons_py2_Qt4 as icons


# TODO : make py3_Qt4 (normally never the case)

