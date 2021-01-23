
import ephyviewer
import numpy as np
import os

from ephyviewer.tests.testing_tools import get_tdt_test_files


def test_neoviewer():
    from neo.rawio.tdtrawio import TdtRawIO

    local_test_dir = get_tdt_test_files()
    dirname = os.path.join(local_test_dir, 'aep_05')
    neorawio = TdtRawIO(dirname=dirname)
    neorawio.parse_header()
    print(neorawio)

    sources = ephyviewer.get_sources_from_neo_rawio(neorawio)


    app = ephyviewer.mkQApp()
    win = ephyviewer.MainViewer(debug=True, show_auto_scale=True)

    for i, sig_source in enumerate(sources['signal']):
        view = ephyviewer.TraceViewer(source=sig_source, name='signal {}'.format(i))
        win.add_view(view)

    for i, ep_source in enumerate(sources['epoch']):
        view = ephyviewer.EpochViewer(source=ep_source, name='epochs')
        win.add_view(view)

    win.show()

    app.exec_()



if __name__=='__main__':
    test_neoviewer()
