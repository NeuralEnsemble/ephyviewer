
import ephyviewer
import numpy as np
import os



def test_neoviewer():
    #TODO make autorun neo tdtrawio test before
    from neo.rawio.tdtrawio import TdtRawIO
    
    dirname = '/tmp/files_for_testing_neo/tdt/aep_05/'
    neorawio = TdtRawIO(dirname=dirname)
    neorawio.parse_header()
    print(neorawio)
    
    sources = ephyviewer.get_source_from_neo(neorawio)
    

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