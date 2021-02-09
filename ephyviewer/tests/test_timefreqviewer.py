import ephyviewer


from  ephyviewer.tests.testing_tools import make_fake_signals


def test_timefreqviewer(interactive=False):
    source = make_fake_signals()


    app = ephyviewer.mkQApp()
    view = ephyviewer.TimeFreqViewer(source=source, name='timefreq')
    #~ view.refresh()

    #~ for c in range(source.nb_channel):
        #~ view.by_channel_params['ch'+str(c), 'visible'] = True

    win = ephyviewer.MainViewer(debug=True, show_auto_scale=True)
    win.add_view(view)

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()


if __name__=='__main__':
    test_timefreqviewer(interactive=True)
