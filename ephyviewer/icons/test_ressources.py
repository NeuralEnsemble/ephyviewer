 
import sys
from ephyviewer import QT, mkQApp, QT_MODE
print('QT_MODE', QT_MODE)



if __name__ == '__main__' :
	app = mkQApp()
	
	w = QT.QWidget()
	w.show()
	w.setWindowIcon(QT.QIcon(':/media-playback-start.svg'))
	
	app.exec_()
	
	
