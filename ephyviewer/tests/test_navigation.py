import ephyviewer



def test_base():
    app = ephyviewer.mkQApp()
    toolbar = ephyviewer.NavigationToolBar()
    toolbar.show()
    app.exec_()
    
    
    
if __name__=='__main__':
    test_base()

