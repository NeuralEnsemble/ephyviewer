
import ephyviewer
import numpy as np
import os

# get_tdt_test_files
from ephyviewer.tests.testing_tools import get_blackrock_files


def test_neoviewer(interactive=False):
    #~ from neo.rawio.tdtrawio import TdtRawIO

    #~ local_tdt_folder = get_tdt_test_files()
    #~ neorawio = TdtRawIO(dirname=local_tdt_folder)
    #~ neorawio.parse_header()
    #~ print(neorawio)

    from neo.rawio.blackrockrawio import BlackrockRawIO
    filename = get_blackrock_files()
    neorawio = BlackrockRawIO(filename=filename)
    neorawio.parse_header()
    print(neorawio)
    

    sources = ephyviewer.get_sources_from_neo_rawio(neorawio)
    print(sources)


    app = ephyviewer.mkQApp()
    win = ephyviewer.MainViewer(debug=True, show_auto_scale=True)

    for i, sig_source in enumerate(sources['signal']):
        view = ephyviewer.TraceViewer(source=sig_source, name='signal {}'.format(i))
        win.add_view(view)

    for i, ep_source in enumerate(sources['epoch']):
        view = ephyviewer.EpochViewer(source=ep_source, name='epochs')
        win.add_view(view)

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()



if __name__=='__main__':
    test_neoviewer(interactive=True)
