import cv2, json, os, subprocess, asyncio, qasync, sys
from datetime import datetime
from enum import Enum
from mainWindow import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap

APP_TITLE = 'FindFrame'
VERSION = '0.0.1'
WINDOW_TITLE = "{} {}".format(APP_TITLE, VERSION)

# Max number of frames to process at a time
MAX_BATCH_SIZE = 3

def open_image_path():
    path = QtWidgets.QFileDialog.getOpenFileName(None, "Select Image", os.getcwd(), "Images (*.png *.jpg);;idgaf (*.*)")
    if not path[0]:
        print("No image selected!")
        return
    ui.fieldInputImage.setText(os.path.normpath(path[0]))
    asyncio.ensure_future(analyze_image(path[0]))

def open_video_path():
    path = QtWidgets.QFileDialog.getOpenFileName(None, "Select Video", os.getcwd(), "Videos (*.mp4 *.mkv *.webm);;idgaf (*.*)")
    if not path[0]:
        print("No video selected!")
        return
    ui.fieldVideo.setText(os.path.normpath(path[0]))

async def analyze_image(image):
    parsed_image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    
    height, width = parsed_image.shape
    bytesPerLine = 1 * width
    qImg = QImage(parsed_image.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
    aspectFitPixmap = QPixmap(qImg).scaled(ui.imageInput.width(), \
                                        ui.imageInput.height(), \
                                        QtCore.Qt.KeepAspectRatio, \
                                        QtCore.Qt.FastTransformation)
    ui.imageInput.setPixmap(QPixmap(aspectFitPixmap))
    
    orb = cv2.ORB_create()
    keypoints, descriptors = await loop.run_in_executor(None, orb.detectAndCompute, parsed_image, None)
    #brute_force_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    #matches = brute_force_matcher.match(source_descriptors, target_descriptors)

async def scan_video():
    log('Starting processing...')
    set_processing_mode(True)
    path = ui.fieldVideo.text()
    video = cv2.VideoCapture(path)
    if not video.isOpened():
        log("Failed to open {}".format(os.path.basename(path)))
        return

    # Get frame count
    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    log("Total frames: {}".format(total_frames))

    ui.progressBar.setTextVisible(True)
    ui.progressBar.setValue(0)
    ui.progressBar.setRange(0, int(total_frames))

    frameWidth = ui.imageVideoFrame.width()
    frameHeight = ui.imageVideoFrame.height()

    #task = asyncio.ensure_future(process_frame(frameWidth, frameHeight, video, asyncio_semaphore))
    #task.add_done_callback(frame_processing_complete)
    
    while video.isOpened():
        result = await loop.run_in_executor(None, process_frame, frameWidth, frameHeight, video)
        if result:
            ui.imageVideoFrame.setPixmap(result)
            progress = ui.progressBar.value()
            ui.progressBar.setValue(progress + 1)
        else:
            set_processing_mode(False)
            log('Processing complete.')
            ui.progressBar.setValue(ui.progressBar.maximum())
            break
    #time = video.get(cv2.CAP_PROP_POS_MSEC)
    #log("Time at frame 10: {}".format(time))

def frame_processing_complete(status):
    print(status)
    #set_processing_mode(False)
    #log('Finished processing.')
    #ui.imageVideoFrame.setPixmap(aspectFitPixmap)
    #progress = ui.progressBar.value()
    #ui.progressBar.setValue(progress + 1)

def process_frame(scaledWidth, scaledHeight, video):
    #video.set(cv2.CAP_PROP_POS_FRAMES, 10) # Seek to frame 10
    success, frame = video.read()
    if not success:
        return None
    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    height, width, channel = rgbImage.shape
    qImg = QImage(rgbImage.data, width, height, QImage.Format_RGB888)
    return QPixmap(qImg).scaled(scaledWidth, \
                                        scaledHeight, \
                                        QtCore.Qt.KeepAspectRatio, \
                                        QtCore.Qt.FastTransformation)

def start_processing():
    if not ui.fieldInputImage.text() or not ui.fieldVideo.text():
        log('<span style="color:red;">Error: Must have both a source image and target video!</span>')
        return

    if ui.btnStartScan.text() == "Cancel":
        pending_tasks = asyncio.all_tasks(loop)
        for task in pending_tasks:
            task.cancel()
        log('Cancelled!')
        set_processing_mode(False)
    else:
        task = asyncio.ensure_future(scan_video())
        task.add_done_callback(frame_processing_complete)

def set_processing_mode(processing):
    if processing:
        ui.btnStartScan.setText("Cancel")
    else:
        ui.btnStartScan.setText("Scan Video")

    ui.progressBar.setTextVisible(processing)

def log(message):
    ui.textLog.append("[{}] {}".format(datetime.now().strftime("%H:%M:%S.%f"), message))

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
app = QtWidgets.QApplication(sys.argv)
loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)
asyncio.events._set_running_loop(loop)
asyncio_semaphore = asyncio.Semaphore(MAX_BATCH_SIZE)

MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)

# EVENTS
ui.btnOpenInputImage.clicked.connect(open_image_path)
ui.btnOpenVideo.clicked.connect(open_video_path)
ui.btnStartScan.clicked.connect(start_processing)

MainWindow.setWindowTitle(WINDOW_TITLE)
MainWindow.show()

with loop:
    loop.run_forever()