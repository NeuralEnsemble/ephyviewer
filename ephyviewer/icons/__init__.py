import sys
from ephyviewer.myqt import QT_MODE

if QT_MODE == 'PyQt5':
    from . import icons_PyQt5 as icons
elif QT_MODE == 'PySide2':
    from . import icons_PySide2 as icons
elif QT_MODE == 'PyQt4':
    from . import  icons_PyQt4 as icons
else:
    raise ValueError('Could not load icons for unrecognized QT_MODE: ' + QT_MODE)
