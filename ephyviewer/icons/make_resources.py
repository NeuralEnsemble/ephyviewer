import os
import sys


def make_resources_icons(qt_mode):
    with open('icons.qrc','w') as f:
        f.write("""<!DOCTYPE RCC><RCC version="1.0">
    <qresource>
""")
        for p, d, files in os.walk('./'):
            for filename in files:
                if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.svg'):
                    f.write('            <file alias="%s">%s/%s</file>\r\n' % (filename, p[2:],filename) )

        f.write("""    </qresource>
</RCC>
""")

    if qt_mode == 'PyQt5':
        os.popen('pyrcc5 icons.qrc -o icons_PyQt5.py')

    elif qt_mode == 'PySide2':
        os.popen('pyside2-rcc icons.qrc -o icons_PySide2.py')

    elif qt_mode == 'PyQt4':
        os.popen('pyrcc4 -py3 icons.qrc -o icons_PyQt4.py')

    else:
        raise ValueError('Cannot build icons for unrecognized Qt bindings: ' + qt_mode)


#------------------------------------------------------------------------------
if __name__ == '__main__' :

    if len(sys.argv) > 1:
        qt_mode = sys.argv[1]
    else:
        from ephyviewer.myqt import QT_MODE as qt_mode

    print('Building icons for Qt bindings:', qt_mode)
    make_resources_icons(qt_mode)
