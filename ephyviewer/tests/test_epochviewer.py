import ephyviewer


from  ephyviewer.tests.testing_tools import make_fake_epoch_source


def test_epoch_viewer(interactive=False):
    source = make_fake_epoch_source()


    app = ephyviewer.mkQApp()
    view = ephyviewer.EpochViewer(source=source, name='epoch')

    win = ephyviewer.MainViewer(debug=True)
    win.add_view(view)

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()


if __name__=='__main__':
    test_epoch_viewer(interactive=True)
