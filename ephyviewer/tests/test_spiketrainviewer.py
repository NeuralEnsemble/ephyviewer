import ephyviewer


from  ephyviewer.tests.testing_tools import make_fake_spiketrain_source


def test_spiketrain_viewer(interactive=False):
    source = make_fake_spiketrain_source()


    app = ephyviewer.mkQApp()
    view = ephyviewer.SpikeTrainViewer(source=source, name='spikes')

    win = ephyviewer.MainViewer(debug=True)
    win.add_view(view)

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()


if __name__=='__main__':
    test_spiketrain_viewer(interactive=True)
