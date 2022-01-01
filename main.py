import cv2, json, os, subprocess, asyncio, quamash, sys
from enum import Enum
from mainWindow import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap

APP_TITLE = 'FindFrame'
VERSION = '0.0.1'

def open_image_path():
    path = QtWidgets.QFileDialog.getOpenFileName(None, "Select Image", os.getcwd(), "Images (*.png *.jpg);;idgaf (*.*)")
    if not path[0]:
        print("No image selected!")
        return
    ui.fieldInputImage.setText(os.path.normpath(path[0]))
    analyze_image(path[0])

def open_video_path():
    path = QtWidgets.QFileDialog.getOpenFileName(None, "Select Video", os.getcwd(), "Videos (*.mp4 *.mkv *.webm);;idgaf (*.*)")
    if not path[0]:
        print("No video selected!")
        return
    ui.fieldVideo.setText(os.path.normpath(path[0]))
    ui.textLog.append("Opened video {}".format(os.path.basename(path[0])))

    video = cv2.VideoCapture(path[0])
    if not video.isOpened():
        ui.textLog.append("Failed to open {}".format(os.path.basename(path[0])))
        return

    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT) # 7 = prop-id
    ui.textLog.append("Total frames: {}".format(total_frames))

    video.set(cv2.CAP_PROP_POS_FRAMES, 10) # Seek to frame 10
    success, frame = video.read()
    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    height, width, channel = rgbImage.shape
    qImg = QImage(rgbImage.data, width, height, QImage.Format_RGB888)
    aspectFitPixmap = QPixmap(qImg).scaled(ui.imageVideoFrame.width(), \
                                           ui.imageVideoFrame.height(), \
                                           QtCore.Qt.KeepAspectRatio, \
                                           QtCore.Qt.FastTransformation)
    ui.imageVideoFrame.setPixmap(aspectFitPixmap)
    time = video.get(cv2.CAP_PROP_POS_MSEC)
    ui.textLog.append("Time at frame 10: {}".format(time))

def analyze_image(image):
    parsed_image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    
    height, width = parsed_image.shape
    bytesPerLine = 1 * width
    qImg = QImage(parsed_image.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
    aspectFitPixmap = QPixmap(qImg).scaled(ui.imageVideoFrame.width(), \
                                        ui.imageVideoFrame.height(), \
                                        QtCore.Qt.KeepAspectRatio, \
                                        QtCore.Qt.FastTransformation)
    ui.imageInput.setPixmap(QPixmap(aspectFitPixmap))
    ui.textLog.append('Parsed input image.')
    
    orb = cv2.ORB_create()
    keypoints, descriptors = orb.detectAndCompute(parsed_image, None)
    brute_force_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = brute_force_matcher.match(descriptors, descriptors)
    return

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
app = QtWidgets.QApplication(sys.argv)
loop = quamash.QEventLoop(app)
asyncio.set_event_loop(loop)

MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)

# EVENTS
ui.btnOpenInputImage.clicked.connect(open_image_path)
ui.btnOpenVideo.clicked.connect(open_video_path)

MainWindow.setWindowTitle("{} {}".format(APP_TITLE, VERSION))
MainWindow.show()

with loop:
    loop.run_forever()