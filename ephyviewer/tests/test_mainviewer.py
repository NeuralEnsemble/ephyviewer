import ephyviewer

from ephyviewer.base import ViewerBase






def test_mainviewer():

    class FakeView(ViewerBase):
        def refresh(self):
            #~ print('refresh', self.name, self.t)
            pass
    
    app = ephyviewer.mkQApp()
    
    view1 = FakeView(name='view1')
    view2 = FakeView(name='view2')
    view3 = FakeView(name='view3')
    view4 = FakeView(name='view4')
    view5 = FakeView(name='view5')
    
    win = ephyviewer.MainViewer()
    win.add_view(view1)
    win.add_view(view2)
    
    win.add_view(view3, tabify_with='view2')
    win.add_view(view4, split_with='view1', orientation='horizontal')
    win.add_view(view5, location='bottom',  orientation='horizontal')
    
    win.show()
    app.exec_()

def test_mainviewer2():
    from  ephyviewer.tests.testing_tools import make_fake_video_source
    from  ephyviewer.tests.testing_tools import make_fake_signals
    from  ephyviewer.tests.testing_tools import make_event_source
    
    
    app = ephyviewer.mkQApp()
    
    view1 = ephyviewer.TraceViewer(source=make_fake_signals(), name='signals')
    view2 = ephyviewer.VideoViewer(source=make_fake_video_source(), name='video')
    view3 = ephyviewer.EventList(source=make_event_source(), name='events')
    
    win = ephyviewer.MainViewer()
    win.add_view(view1)
    win.add_view(view2)
    win.add_view(view3, location='bottom',  orientation='horizontal')
    
    win.show()
    app.exec_()


    
    
    
if __name__=='__main__':
    #~ test_mainviewer()
    test_mainviewer2()

