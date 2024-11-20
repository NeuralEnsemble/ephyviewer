import ephyviewer
from ephyviewer.tests.testing_tools import make_fake_signals


# Create the main Qt application (for event loop)
app = ephyviewer.mkQApp()

# Create the main window that can contain several viewers
win = ephyviewer.MainViewer(debug=True, show_auto_scale=True)

# Create a TraceView and add it to the main window
view1 = ephyviewer.TraceViewer(source=make_fake_signals(), name="LFPs")
view1.params["scale_mode"] = "same_for_all"
win.add_view(view1)

# Create a TraceImageView and add it to the main window
view2 = ephyviewer.TraceImageViewer(source=make_fake_signals(), name="CSDs")
win.add_view(view2)

# show main window and run Qapp
win.show()
app.exec()
