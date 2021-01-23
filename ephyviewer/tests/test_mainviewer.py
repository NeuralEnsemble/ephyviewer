import ephyviewer

from ephyviewer.base import ViewerBase






def test_mainviewer(interactive=False):

    class FakeView(ViewerBase):
        def __init__(self, name=''):
            ViewerBase.__init__(self, name)
            self.v = None
        def refresh(self):
            self.v = self.t
            #~ print('refresh', self.name, self.t)
            pass
        def set_settings(self, value):
            self.v = value
        def get_settings(self):
            return self.v

    app = ephyviewer.mkQApp()

    view1 = FakeView(name='view1')
    view2 = FakeView(name='view2')
    view3 = FakeView(name='view3')
    view4 = FakeView(name='view4')
    view5 = FakeView(name='view5')

    win = ephyviewer.MainViewer(settings_name='test0')
    win.add_view(view1)
    win.add_view(view2)

    win.add_view(view3, tabify_with='view2')
    win.add_view(view4, split_with='view1', orientation='horizontal')
    win.add_view(view5, location='bottom',  orientation='horizontal')

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()

def test_mainviewer2(interactive=False):
    from  ephyviewer.tests.testing_tools import make_fake_video_source
    from  ephyviewer.tests.testing_tools import make_fake_signals
    from  ephyviewer.tests.testing_tools import make_fake_event_source
    from  ephyviewer.tests.testing_tools import make_fake_epoch_source


    app = ephyviewer.mkQApp()

    view1 = ephyviewer.TraceViewer(source=make_fake_signals(), name='signals')
    view2 = ephyviewer.VideoViewer(source=make_fake_video_source(), name='video')
    view3 = ephyviewer.EventList(source=make_fake_event_source(), name='events')
    view4 = ephyviewer.EpochViewer(source=make_fake_epoch_source(), name='epoch')
    view5 = ephyviewer.TimeFreqViewer(source=make_fake_signals(), name='timefreq')


    win = ephyviewer.MainViewer(debug=True, settings_name='test1', show_global_xsize=True, show_auto_scale=True)
    #TODO bug because new params!!!!!!!
    #~ win = ephyviewer.MainViewer(debug=True, show_global_xsize=True)
    win.add_view(view1)
    win.add_view(view5)
    win.add_view(view2)
    win.add_view(view4)
    win.add_view(view3, location='bottom',  orientation='horizontal')

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()


def test_save_load_params(interactive=False):
    from  ephyviewer.tests.testing_tools import make_fake_signals


    app = ephyviewer.mkQApp()

    view1 = ephyviewer.TraceViewer(source=make_fake_signals(), name='signals')

    win = ephyviewer.MainViewer(debug=True, settings_name='test2', show_global_xsize=True, show_auto_scale=True)
    #~ print(win.settings_name)
    #~ exit()
    #TODO bug because new params!!!!!!!
    win.add_view(view1)

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()



if __name__=='__main__':
    test_mainviewer(interactive=True)
    test_mainviewer2(interactive=True)
    test_save_load_params(interactive=True)
