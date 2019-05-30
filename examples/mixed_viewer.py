import ephyviewer

#for this example we use fake source construct by theses function
from  ephyviewer.tests.testing_tools import make_fake_video_source
from  ephyviewer.tests.testing_tools import make_fake_signals
from  ephyviewer.tests.testing_tools import make_fake_event_source
from  ephyviewer.tests.testing_tools import make_fake_epoch_source

sig_source = make_fake_signals()
event_source = make_fake_event_source()
epoch_source = make_fake_epoch_source()
video_source = make_fake_video_source()



app = ephyviewer.mkQApp()
view1 = ephyviewer.TraceViewer(source=sig_source, name='signals')
view2 = ephyviewer.VideoViewer(source=video_source, name='video')
view3 = ephyviewer.EventList(source=event_source, name='events')
view4 = ephyviewer.EpochViewer(source=epoch_source, name='epoch')
view5 = ephyviewer.TimeFreqViewer(source=sig_source, name='timefreq')


win = ephyviewer.MainViewer(debug=True, settings_name='test1', show_global_xsize=True, show_auto_scale=True)

win.add_view(view1)
win.add_view(view5, split_with='signals')
win.add_view(view2)
win.add_view(view4)
win.add_view(view3, location='bottom',  orientation='horizontal')

win.show()

win.auto_scale()

app.exec_()
