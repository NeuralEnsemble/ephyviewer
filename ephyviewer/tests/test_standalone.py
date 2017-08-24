


from ephyviewer.standalone import StandAloneViewer, RawNeoOpenDialog
import pyqtgraph as pg



def test_StandAloneViewer():
    app = pg.mkQApp()
    win = StandAloneViewer()
    win.show()
    app.exec_()


def test_RawNeoOpenDialog():
    app = pg.mkQApp()
    dia = RawNeoOpenDialog()
    dia.show()
    app.exec_()
    
    print(dia.final_params)



if __name__=='__main__':
    test_StandAloneViewer()
    #~ test_RawNeoOpenDialog()
