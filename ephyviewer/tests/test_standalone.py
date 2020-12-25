


from ephyviewer.standalone import WindowManager, RawNeoOpenDialog
import pyqtgraph as pg



def test_WindowManager():
    app = pg.mkQApp()
    manager = WindowManager()
    manager.open_dialog()
    if manager.windows:
        app.exec_()


def test_RawNeoOpenDialog():
    app = pg.mkQApp()
    dia = RawNeoOpenDialog()
    dia.show()
    app.exec_()

    print(dia.final_params)



if __name__=='__main__':
    test_WindowManager()
    #~ test_RawNeoOpenDialog()
