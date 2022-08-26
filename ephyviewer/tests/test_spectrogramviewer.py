import ephyviewer

import numpy as np
from  ephyviewer.tests.testing_tools import make_fake_signals


def test_spectrogramviewer(interactive=False):
    
    
    app = ephyviewer.mkQApp()
    
    fs = sample_rate = 100000.
    times = np.arange(0, 100., 1./sample_rate, dtype='float64')
    sigs = np.random.randn(times.size, 2) * 2.
    sigs[:, 0] += np.sin(times * 2 * np.pi *5000.) * 1.5
    sigs[:, 1] += np.sin(times * 2 * np.pi *20000.) * 0.5


    #create moving sinus
    sigsize = times.size
    f1 = 1000.
    f2 = 25000.
    freqs1 = np.concatenate([np.linspace(0,.5,sigsize*3//8) *  (f2-f1) + f1, np.ones(sigsize//4)*(f1+f2)/2 , np.linspace(0,.5,sigsize*3//8) *  (f2-f1) + (f1+f2)/2], axis=0)
    phase1 = np.cumsum(freqs1/fs)*2*np.pi
    sigs[:, 0] += np.sin(phase1)
    
    t_start = 0.
    name = 'spectrogram'
    view = ephyviewer.SpectrogramViewer.from_numpy( sigs, sample_rate, t_start, name, channel_names=None)
    
    win = ephyviewer.MainViewer(debug=True, show_auto_scale=True)
    win.add_view(view)
    
    
    # view2 = ephyviewer.TraceViewer.from_numpy(sigs, sample_rate, t_start, 'sigs', channel_names=None)
    # win.add_view(view2)

    if interactive:
        win.show()
        app.exec()
    else:
        # close thread properly
        win.close()


if __name__=='__main__':
    test_spectrogramviewer(interactive=True)
