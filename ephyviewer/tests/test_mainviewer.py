import ephyviewer

from ephyviewer.base import ViewerBase


class FakeView(ViewerBase):
    pass



def test_mainviewer():
    app = ephyviewer.mkQApp()
    
    view1 = FakeView()
    view2 = FakeView()
    
    win = ephyviewer.MainViewer()
    win.add_view(view1, 'view1')
    win.add_view(view2, 'view2')
    
    win.show()
    app.exec_()
    
    
    
    
if __name__=='__main__':
    test_mainviewer()