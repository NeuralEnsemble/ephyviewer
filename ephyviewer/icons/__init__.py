import sys
from ephyviewer.myqt import QT_MODE

if QT_MODE == 'PyQt5':
    from . import  icons_PyQt5 as icons
elif QT_MODE == 'PyQt4':
    from . import  icons_PyQt4 as icons
