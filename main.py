import cv2, json, math, os, subprocess, asyncio, qasync, sys
from datetime import datetime
from enum import Enum
from mainWindow import Ui_MainWindow
from resultsWindow import Ui_ResultsWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QTableWidgetItem

APP_TITLE = 'FindFrame'
VERSION = '0.0.1'
WINDOW_TITLE = "{} {}".format(APP_TITLE, VERSION)

class ResultsColumns(Enum):
    TIMESTAMP = 0
    THUMBNAIL = 1

match_threshold = 40 # Percent of matching descriptors

def millisToTime(ms):
    x = ms / 1000
    seconds = round(x % 60)
    x /= 60
    minutes = math.floor(x % 60)
    x /= 60
    hours = math.floor(x % 24)
    return "{}:{}:{}".format(str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2))

def open_image_path():
    working_dir = ui.fieldInputImage.text()
    if len(working_dir) == 0 or not os.path.exists(working_dir):
        working_dir = os.getcwd()
    path = QtWidgets.QFileDialog.getOpenFileName(None, "Select Image", working_dir, \
        "Images (*.png *.jpg);;idgaf (*.*)")
    if not path[0]:
        print("No image selected!")
        return
    ui.fieldInputImage.setText(os.path.normpath(path[0]))
    analyze_image(path[0])

def open_video_path():
    working_dir = ui.fieldVideo.text()
    if len(working_dir) == 0 or not os.path.exists(working_dir):
        working_dir = os.getcwd()
    path = QtWidgets.QFileDialog.getOpenFileName(None, "Select Video", working_dir, \
        "Videos (*.mp4 *.mkv *.webm);;idgaf (*.*)")
    if not path[0]:
        print("No video selected!")
        return
    ui.fieldVideo.setText(os.path.normpath(path[0]))

def analyze_image(image):
    parsed_image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    
    height, width = parsed_image.shape
    bytesPerLine = 1 * width
    qImg = QImage(parsed_image.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
    aspectFitPixmap = QPixmap(qImg).scaled(ui.imageInput.width(), \
                                        ui.imageInput.height(), \
                                        QtCore.Qt.KeepAspectRatio, \
                                        QtCore.Qt.FastTransformation)
    ui.imageInput.setPixmap(aspectFitPixmap)

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
    log("Total frames: {}".format(int(total_frames)))

    ui.progressBar.setTextVisible(True)
    ui.progressBar.setValue(0)
    ui.progressBar.setRange(0, int(total_frames))

    frameWidth = ui.imageVideoFrame.width()
    frameHeight = ui.imageVideoFrame.height()

    # Only need to get source image and generate descriptors once
    source_frame = cv2.imread(ui.fieldInputImage.text(), cv2.IMREAD_GRAYSCALE)
    
    log('Generating source image descriptors...')
    orb = cv2.ORB_create()
    keypoints, descriptors = await loop.run_in_executor(None, orb.detectAndCompute, source_frame, None)
    brute_force_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    log('Descriptor count for source frame: {}'.format(len(descriptors)))

    # Clear out results table
    results_ui.resultsTable.setRowCount(0)

    log('Beginning match search...')
    candidate_frames = set()
    while video.isOpened():
        result, timestamp, bad_frame = await loop.run_in_executor(None, process_frame, frameWidth, frameHeight, \
            orb, brute_force_matcher, descriptors, video)
        if bad_frame:
            progress = ui.progressBar.value()
            ui.progressBar.setValue(progress + 1)
        elif result:
            ui.imageVideoFrame.setPixmap(result)
            progress = ui.progressBar.value()
            ui.progressBar.setValue(progress + 1)
            if timestamp > -1:
                print(timestamp)
                converted_timestamp = millisToTime(timestamp)
                candidate_frames_prev_size = len(candidate_frames)
                candidate_frames.add(converted_timestamp)
                # New timestamp, so include in results table
                if len(candidate_frames) > candidate_frames_prev_size:
                    results_ui.resultsTable.setRowCount(results_ui.resultsTable.rowCount() + 1)
                    thumbnail_label = QLabel()
                    thumbnail_label.setAlignment(QtCore.Qt.AlignCenter)
                    thumbnail_label.setPixmap(result)
                    timestamp_item = QTableWidgetItem(converted_timestamp)
                    timestamp_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    results_ui.resultsTable.setItem(results_ui.resultsTable.rowCount() - 1, 0, timestamp_item)
                    results_ui.resultsTable.setCellWidget(results_ui.resultsTable.rowCount() - 1, 1, thumbnail_label)
                    log('Possible match at {}'.format(converted_timestamp))
        else:
            set_processing_mode(False)
            log('Processing complete.')
            if len(candidate_frames) > 0:
                candidate_frames = sorted(candidate_frames)
                log('Found likely matches at: {}'.format(list(candidate_frames)))
                ResultsWindow.exec_()
            else:
                log('Did not find any matches!')
            ui.progressBar.setValue(ui.progressBar.maximum())
            break

def frame_processing_complete(status):
    print(status)
 
def process_frame(scaledWidth, scaledHeight, orb, brute_force_matcher, source_descriptors, video):
    #video.set(cv2.CAP_PROP_POS_FRAMES, 10) # Seek to frame 10
    timestamp = -1
    success, frame = video.read()
    if not success:
        return None, timestamp, False
    
    if not frame.any():
        print('Bad frame')
        return None, timestamp, True

    frame_number = video.get(cv2.CAP_PROP_POS_FRAMES)
    
    #rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    height, width = image.shape
    if height <= 0 or width <= 0:
        # Discard bad frame
        print('Bad frame')
        return None, timestamp, True

    # Generate frame desciptors
    keypoints, descriptors = orb.detectAndCompute(image, None)

    if descriptors is None: # This is absolutely idiotic syntax
        # Discard frame with no descriptors (this can be blank or corrupt frames)
        return None, timestamp, True

    matches = brute_force_matcher.match(source_descriptors, descriptors)
    print('Matches for frame {}: {}'.format(frame_number, len(matches)))

    if len(matches) > (len(source_descriptors) * (match_threshold / 100)):
        # Likely match, so get timestamp
        timestamp = video.get(cv2.CAP_PROP_POS_MSEC)

    qImg = QImage(image.data, width, height, width, QImage.Format_Grayscale8)
    return QPixmap(qImg).scaled(scaledWidth, \
                                        scaledHeight, \
                                        QtCore.Qt.KeepAspectRatio, \
                                        QtCore.Qt.FastTransformation), timestamp, False

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
    ui.btnOpenInputImage.setEnabled(not processing)
    ui.btnOpenVideo.setEnabled(not processing)
    ui.sliderMatchThresh.setEnabled(not processing)

def match_thresh_changed():
    global match_threshold
    match_threshold = ui.sliderMatchThresh.value()
    ui.labelMatchThresh.setText("{}%".format(match_threshold))

def log(message):
    ui.textLog.append("[{}] {}".format(datetime.now().strftime("%H:%M:%S.%f"), message))

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
app = QtWidgets.QApplication(sys.argv)
loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)
asyncio.events._set_running_loop(loop)

MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)

ResultsWindow = QtWidgets.QDialog(MainWindow)
results_ui = Ui_ResultsWindow()
results_ui.setupUi(ResultsWindow)

results_ui.resultsTable.setHorizontalHeaderLabels(['Timestamp', 'Thumbnail'])


# Defaults
ui.sliderMatchThresh.setSliderPosition(match_threshold)
ui.labelMatchThresh.setText("{}%".format(match_threshold))

# EVENTS
ui.btnOpenInputImage.clicked.connect(open_image_path)
ui.btnOpenVideo.clicked.connect(open_video_path)
ui.btnStartScan.clicked.connect(start_processing)
ui.sliderMatchThresh.valueChanged.connect(match_thresh_changed)

ui.testbutton.clicked.connect(lambda: ResultsWindow.exec_())

MainWindow.setWindowTitle(WINDOW_TITLE)
MainWindow.show()

with loop:
    loop.run_forever()