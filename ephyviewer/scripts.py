
import sys
import os
import argparse
from ephyviewer.datasource import HAVE_NEO
from ephyviewer.standalone import all_neo_rawio_dict, rawio_gui_params
from ephyviewer import __version__

def launch_standalone_ephyviewer():
    from ephyviewer.standalone import WindowManager
    import pyqtgraph as pg
    assert HAVE_NEO, 'Must have Neo >= 0.6.0'
    import neo


    argv = sys.argv[1:]

    description = """
    Visualize electrophysiological data stored in files readable with Neo's
    RawIO classes
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('file_or_dir', default=None, nargs='?',
                        help='an optional path to a data file or directory, '
                             'which will be opened immediately (the file '
                             'format will be inferred from the file '
                             'extension, if possible; otherwise, --format is '
                             'required)')
    parser.add_argument('-V', '--version', action='version',
                        version='ephyviewer {}'.format(__version__))
    parser.add_argument('-f', '--format', default=None,
                        help='specify one of the following formats to '
                             'override the format detected automatically for '
                             'file_or_dir: {}'.format(
                             ', '.join(all_neo_rawio_dict.keys())))

    app = pg.mkQApp()

    manager = WindowManager()

    if len(argv)>=1:
        args = parser.parse_args(argv)
        file_or_dir_name = args.file_or_dir

        if args.format is None:
            #autoguess from extension
            neo_rawio_class = neo.rawio.get_rawio_class(file_or_dir_name)
        else:
            neo_rawio_class = all_neo_rawio_dict.get(args.format, None)

        assert neo_rawio_class is not None, 'Unknown format. Format list: {}'.format(', '.join(all_neo_rawio_dict.keys()))

        name = neo_rawio_class.__name__.replace('RawIO', '')
        if name in rawio_gui_params:
            raise(Exception('This IO requires additional parameters. Run ephyviewer without arguments to input these via the GUI.'))

        manager.load_dataset(neo_rawio_class=neo_rawio_class, file_or_dir_names=[file_or_dir_name])

    else:
        manager.open_dialog()

    if manager.windows:
        app.exec_()

if __name__=='__main__':
    launch_standalone_ephyviewer()
