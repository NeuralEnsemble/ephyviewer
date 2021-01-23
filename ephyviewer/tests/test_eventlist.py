import ephyviewer


from  ephyviewer.tests.testing_tools import make_fake_event_source


def test_eventlist(interactive=False):
    source = make_fake_event_source()


    app = ephyviewer.mkQApp()
    view = ephyviewer.EventList(source=source, name='events')

    win = ephyviewer.MainViewer(debug=True)
    win.add_view(view)

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()



if __name__=='__main__':
    test_eventlist(interactive=True)
