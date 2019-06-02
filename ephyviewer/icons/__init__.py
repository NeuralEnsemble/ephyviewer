import sys

if sys.version_info > (3,):
    from . import  icons_py3 as icons
else:
    from . import icons

