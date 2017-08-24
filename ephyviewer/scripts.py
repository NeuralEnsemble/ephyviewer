
import sys
import os
import argparse


    
def launch_standalone_ephyviewer():
    from ephyviewer.standalone import StandAloneViewer
    import pyqtgraph as pg
    
    app = pg.mkQApp()
    win = StandAloneViewer()
    win.show()
    app.exec_()

if __name__=='__main__':
    launch_standalone_ephyviewer()

