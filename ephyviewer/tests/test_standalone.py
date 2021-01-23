


from ephyviewer.standalone import WindowManager, RawNeoOpenDialog
import pyqtgraph as pg



def test_WindowManager(interactive=False):
    app = pg.mkQApp()
    manager = WindowManager()

    if interactive:
        manager.open_dialog()
        if manager.windows:
            app.exec_()


def test_RawNeoOpenDialog(interactive=False):
    app = pg.mkQApp()
    dia = RawNeoOpenDialog()

    if interactive:
        dia.show()
        app.exec_()

    print(dia.final_params)



if __name__=='__main__':
    test_WindowManager(interactive=True)
    test_RawNeoOpenDialog(interactive=True)
