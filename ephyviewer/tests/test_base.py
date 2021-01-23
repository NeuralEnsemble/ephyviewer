import ephyviewer
import ephyviewer.base



def test_base(interactive=False):
    app = ephyviewer.mkQApp()
    win = ephyviewer.base.ViewerBase()

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()




if __name__=='__main__':
    test_base(interactive=True)
