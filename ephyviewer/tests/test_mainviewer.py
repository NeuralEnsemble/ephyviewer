import ephyviewer

from ephyviewer.base import ViewerBase


class FakeView(ViewerBase):
    def refresh(self):
        #~ print('refresh', self.name, self.t)
        pass



def test_mainviewer():
    app = ephyviewer.mkQApp()
    
    view1 = FakeView(name='view1')
    view2 = FakeView(name='view2')
    view3 = FakeView(name='view3')
    view4 = FakeView(name='view4')
    
    win = ephyviewer.MainViewer()
    win.add_view(view1)
    win.add_view(view2)
    
    win.add_view(view3, tabify_with='view2')
    win.add_view(view4, split_with='view1', orientation='horizontal')
    
    
    win.show()
    app.exec_()
    
    
    
    
if __name__=='__main__':
    test_mainviewer()

