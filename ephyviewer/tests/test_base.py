import ephyviewer
import ephyviewer.base



def test_base():
    app = ephyviewer.mkQApp()
    win = ephyviewer.base.ViewerBase()
    win.show()
    app.exec_()
    
    
    
    
if __name__=='__main__':
    test_base()