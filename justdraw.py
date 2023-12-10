import sys

from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtGui import QGuiApplication, QImage, QIcon
from PyQt6.QtCore import QTimer, QObject, QUrl, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QMessageBox

from images import ImageList

imgList = ImageList()
imgList.load()

app = QGuiApplication(sys.argv)
app.setWindowIcon(QIcon('./images/icon.png'))

engine = QQmlApplicationEngine()
engine.quit.connect(app.quit)
engine.load('main.qml')


class Backend(QObject):
    # update timer value in the upper right corner
    setcurtimer = pyqtSignal(str, str, arguments=['cur_timer, color'])

    # set current image
    setcurimage = pyqtSignal(str, arguments=['img_path'])

    # set current image flipped horizontally
    setcurimagemirror = pyqtSignal(str, arguments=['img_path'])

    # set window size from command line parameters
    setwindowsize = pyqtSignal(int, int, arguments=['w, h'])

    def __init__(self):
        super().__init__()

        # Define timer.
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.set_cur_timer)
        self.timer.start()

    def set_cur_timer(self):
        global imgList
        cur_timer = imgList.getCurTimer()

        if cur_timer == 'expired':
            # set new image
            self.reload()

            # get new timer value
            cur_timer = imgList.getCurTimer(False)

        self.setcurtimer.emit(cur_timer, imgList.getCurTimerColor())

    def windowsize(self):
        self.setwindowsize.emit(512, 860)

    def reload(self, mirror=False):
        global imgList

        if mirror:
            self.setcurimagemirror.emit(QUrl.fromLocalFile(imgList.getImagePath()).path())
        else:
            self.setcurimage.emit(QUrl.fromLocalFile(imgList.getImagePath()).path())

    @pyqtSlot()
    def prev_in_folder(self):
        global imgList
        imgList.change(-2)
        self.reload()

    @pyqtSlot()
    def prev(self):
        global imgList
        imgList.change(-1)
        self.reload()

    @pyqtSlot()
    def next(self):
        global imgList
        imgList.change(1)
        self.reload()

    @pyqtSlot()
    def next_in_folder(self):
        global imgList
        imgList.change(2)
        self.reload()

    @pyqtSlot()
    def pause(self):
        global imgList
        imgList.pause()

    @pyqtSlot()
    def info(self):
        global imgList
        msgBox = QMessageBox()
        msgBox.setText(imgList.getImagePath())
        msgBox.exec()

    @pyqtSlot()
    def prev(self):
        global imgList
        imgList.change(-1)
        self.reload()

    @pyqtSlot()
    def exclude_folder(self):
        global imgList
        imgList.excludeFolder()
        self.reload()

    @pyqtSlot()
    def mirror(self):
        self.reload(mirror=True)

    @pyqtSlot()
    def copy(self):
        global imgList
        app.clipboard().setImage(QImage(imgList.getImagePath()))

# define our backend object, which we pass to QML
backend = Backend()

# some pyqt magic
engine.rootObjects()[0].setProperty('backend', backend)

# apply window size from command line
backend.windowsize()

# this call set first image because initially timer expired
backend.set_cur_timer()

sys.exit(app.exec())
