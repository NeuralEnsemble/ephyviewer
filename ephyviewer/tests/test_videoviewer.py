import ephyviewer


from  ephyviewer.tests.testing_tools import make_fake_video_source


def test_videoviewer(interactive=False):
    source = make_fake_video_source()

    #~ exit()
    #~ print('*'*50)
    app = ephyviewer.mkQApp()
    view = ephyviewer.VideoViewer(source=source, name='video')
    view.params['nb_column'] = 2

    win = ephyviewer.MainViewer(debug=True)
    win.add_view(view)

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()


if __name__=='__main__':
    test_videoviewer(interactive=True)
