
import sys
import os
import argparse
from ephyviewer.datasource import HAVE_NEO
from ephyviewer.standalone import all_neo_rawio_dict, rawio_gui_params
    
def launch_standalone_ephyviewer():
    from ephyviewer.standalone import StandAloneViewer
    import pyqtgraph as pg
    assert HAVE_NEO, 'Must have neo 0.6.0'
    import neo
    
    
    argv = sys.argv[1:]
    
    parser = argparse.ArgumentParser(description='tridesclous')
    parser.add_argument('file_or_dir', help='', default=None, nargs='?')
    parser.add_argument('-f', '--format', help='File format', default=None)
    
    app = pg.mkQApp()
    win = StandAloneViewer()
    win.show()
    
    if len(argv)>=1:
        args = parser.parse_args(argv)
        file_or_dir_name = args.file_or_dir
        
        if args.format is None:
            #autoguess from extension
            neo_rawio_class = neo.rawio.get_rawio_class(file_or_dir_name)
        else:
            neo_rawio_class = all_neo_rawio_dict.get(args.format, None)
            
        assert neo_rawio_class is not None, 'Unknown format. Format list: ['+','.join(all_neo_rawio_dict.keys())+']'
        
        name = neo_rawio_class.__name__.replace('RawIO', '')
        if name in rawio_gui_params:
            raise(Exception('This IO needs arguments. Do ephyviewer and use open menu'))
        
        win.load_dataset(neo_rawio_class=neo_rawio_class, file_or_dir_names=[file_or_dir_name])
        
        
    app.exec_()

if __name__=='__main__':
    launch_standalone_ephyviewer()

