from ephyviewer import QT, mkQApp


def test_icons(interactive=False):
    app = mkQApp()
    w = QT.QWidget()
    w.setWindowIcon(QT.QIcon(':/media-playback-start.svg'))

    if interactive:
    	w.show()
    	app.exec_()


if __name__ == '__main__' :
	test_icons(interactive=True)
