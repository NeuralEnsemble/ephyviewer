import ephyviewer



def test_navigation(interactive=False):
    app = ephyviewer.mkQApp()
    toolbar = ephyviewer.NavigationToolBar()

    if interactive:
        toolbar.show()
        app.exec_()
    else:
        # close thread properly
        toolbar.close()


if __name__=='__main__':
    test_navigation(interactive=True)
