# FindFrame
# Author: Gunbard

from posixpath import join
import cv2, json, math, os, subprocess, asyncio, qasync, sys
from datetime import datetime
from enum import Enum
from mainWindow import Ui_MainWindow
from resultsWindow import Ui_ResultsWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QTableWidgetItem

APP_TITLE = 'FindFrame'
VERSION = '1.0.0'
WINDOW_TITLE = "{} {}".format(APP_TITLE, VERSION)
MATCH_FILTER_THRESHOLD = 0.9 # Discard 10% of possible outlier matches
MULTI_FILE_DELMITER = ';'

# Default number of features to detect in a image or video frame. Default is usually 500, but 1000 provides more 
# usable keypoints on larger images. Increasing this will add processing time.
ORB_NFEATURES = 1000 

# Increase to allow processing more files at once, but progress bars and thumbnails will bug out until the UI is 
# updated in a way that makes sense
MAX_BATCH_SIZE = 1 

# Columns in the Results table
class ResultsColumns(Enum):
    FILENAME = 0
    TIMESTAMP = 1
    CONFIDENCE = 2
    THUMBNAIL = 3

match_threshold = 40 # Default percent of matching descriptors
file_list = [] # List of video files to process


def millisToTime(ms):
    '''
    Helper to convert milliseconds to a timestamp string

    Parameters:
    ms (int): Milliseconds to convert

    Returns:
    string: Ex. "05:30:23"
    '''

    x = ms / 1000
    seconds = round(x % 60)
    x /= 60
    minutes = math.floor(x % 60)
    x /= 60
    hours = math.floor(x % 24)
    return "{}:{}:{}".format(str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2))

def open_image_path():
    '''
    Opens a file chooser dialog to select the source image
    '''

    working_dir = ui.fieldInputImage.text()
    if len(working_dir) == 0 or not os.path.exists(working_dir):
        working_dir = os.getcwd()
    path = QtWidgets.QFileDialog.getOpenFileName(None, "Select image", working_dir, \
        "Images (*.png *.jpg);;idgaf (*.*)")
    if not path[0]:
        print("No image selected!")
        return
    ui.fieldInputImage.setText(os.path.normpath(path[0]))
    analyze_image(path[0])

def open_video_path():
    '''
    Opens a multi-file chooser dialog to select video(s) to scan
    '''

    working_dir = ui.fieldVideo.text()
    if len(working_dir) == 0:
        working_dir = os.getcwd()
    else:
        # If multiple files, just try getting the default dir of the first one
        working_dirs = working_dir.split(MULTI_FILE_DELMITER)
        working_dir = working_dirs[0]
        
    if not os.path.exists(working_dir):
        working_dir = os.getcwd()

    paths = QtWidgets.QFileDialog.getOpenFileNames(None, "Select one or more video files", working_dir, \
        "Videos (*.mp4 *.mkv *.webm);;idgaf (*.*)")
    if not paths[0]:
        print("No video(s) selected!")
        return
    normalized_paths = map(lambda item: os.path.normpath(item), paths[0])
    ui.fieldVideo.setText(MULTI_FILE_DELMITER.join(normalized_paths))

def analyze_image(image):
    '''
    Generates a thumbnail with detected keypoints drawn on the source image

    Parameters:
    image (string): Path to an image file
    '''

    parsed_image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    
    orb = cv2.ORB_create(nfeatures=ORB_NFEATURES)
    keypoints, descriptors = orb.detectAndCompute(parsed_image, None)

    img = cv2.drawKeypoints(parsed_image, keypoints, None, color=(0,255,255), flags=0)

    height, width, channel = img.shape
    bytesPerLine = 3 * width
    qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
    aspectFitPixmap = QPixmap(qImg).scaled(ui.imageInput.width(), \
                                        ui.imageInput.height(), \
                                        QtCore.Qt.KeepAspectRatio, \
                                        QtCore.Qt.FastTransformation)
    ui.imageInput.setPixmap(aspectFitPixmap)

async def scan_video(index, semaphore):
    '''
    Opens a video to process frames. Adds match frames to the results table in the Results window.

    Parameters:
    index (int): Index of the video to scan in file_list
    semaphore (asyncio.Semaphore): Used for async processing
    '''
    
    async with semaphore: 
        global file_list
        path = file_list[index]
        log('Starting processing {}...'.format(os.path.basename(path)))
        set_processing_mode(True)

        video = cv2.VideoCapture(path)
        if not video.isOpened():
            log("Failed to open {}".format(os.path.basename(path)))
            return

        ui.labelFileProgress.setText('File: {}'.format(os.path.basename(path)))
        ui.progressBarFiles.setValue(index + 1)

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
        orb = cv2.ORB_create(nfeatures=ORB_NFEATURES)
        keypoints, descriptors = await loop.run_in_executor(None, orb.detectAndCompute, source_frame, None)

        # Configure flanfly.png matcher
        index_params = dict(algorithm = 6, # FLANN_INDEX_LSH
                        table_number = 6, # 12
                        key_size = 12,     # 20
                        multi_probe_level = 1) # 2
        search_params = dict()

        matcher = cv2.FlannBasedMatcher(index_params, search_params)

        #log('Descriptor count for source frame: {}'.format(len(descriptors)))

        log('Beginning match search...')
        candidate_frames = set() # Using a Set to remove duplicate frames (granularity of one second)
        boost_contrast = ui.checkBoostContrast.isChecked()
        while video.isOpened():
            result, timestamp, bad_frame, matches = await loop.run_in_executor(None, process_frame, \
                frameWidth, frameHeight, \
                matcher, descriptors, video, boost_contrast)
            if bad_frame:
                progress = ui.progressBar.value()
                ui.progressBar.setValue(progress + 1)
            elif result:
                ui.imageVideoFrame.setPixmap(result)
                progress = ui.progressBar.value()
                ui.progressBar.setValue(progress + 1)
                if timestamp > -1:
                    converted_timestamp = millisToTime(timestamp)
                    candidate_frames_prev_size = len(candidate_frames)
                    candidate_frames.add(converted_timestamp)

                    # New timestamp, so include in results table
                    if len(candidate_frames) > candidate_frames_prev_size:
                        results_ui.resultsTable.setRowCount(results_ui.resultsTable.rowCount() + 1)
                        filename_item = QTableWidgetItem(os.path.basename(path))
                        filename_item.setTextAlignment(QtCore.Qt.AlignCenter)
                        thumbnail_label = QLabel()
                        thumbnail_label.setAlignment(QtCore.Qt.AlignCenter)
                        thumbnail_label.setPixmap(result)
                        timestamp_item = QTableWidgetItem(converted_timestamp)
                        timestamp_item.setTextAlignment(QtCore.Qt.AlignCenter)
                        confidence_item = QTableWidgetItem('{:.1f}% ({}/{})'.format(((matches/len(descriptors)) * 100), \
                            matches, len(descriptors)))
                        confidence_item.setTextAlignment(QtCore.Qt.AlignCenter)
                        
                        results_ui.resultsTable.setItem(results_ui.resultsTable.rowCount() - 1, \
                            ResultsColumns.FILENAME.value, filename_item)
                        results_ui.resultsTable.setItem(results_ui.resultsTable.rowCount() - 1, \
                            ResultsColumns.TIMESTAMP.value, timestamp_item)
                        results_ui.resultsTable.setItem(results_ui.resultsTable.rowCount() - 1, \
                            ResultsColumns.CONFIDENCE.value, confidence_item)
                        results_ui.resultsTable.setCellWidget(results_ui.resultsTable.rowCount() - 1, \
                            ResultsColumns.THUMBNAIL.value, thumbnail_label)
                        ResultsWindow.setWindowTitle('{} - Results ({})' \
                            .format(APP_TITLE, results_ui.resultsTable.rowCount()))
                        log('Possible match at {}'.format(converted_timestamp))
            else:
                set_processing_mode(False)
                log('Processing complete.')
                if len(candidate_frames) > 0:
                    candidate_frames = sorted(candidate_frames)
                    log('Found potential matches at: {}'.format(list(candidate_frames)))
                    if not ResultsWindow.isVisible():
                        ResultsWindow.show()
                else:
                    log('Did not find any matches!')
                ui.progressBar.setValue(ui.progressBar.maximum())
                break

def processing_complete(status):
    print(status)
 
def process_frame(scaledWidth, scaledHeight, matcher, source_descriptors, video, boost_contrast):
    '''
    Grabs a frame, compares it to the source image, and if it's within the match threshold, return it as a good match.

    Parameters:
    scaledWidth (int): Thumbnail width for aspect ratio aware scaling
    scaledHeight (int): Thumbnail height for aspect ratio aware scaling
    matcher (cv2 matcher): Magical OpenCV matcher to use for matching
    source_descriptors (array?): OpenCV descriptors generated via ORB thingy
    video (OpenCV VideoCapture): OpenCV handle to the video file
    boost_contrast (bool): Whether or not to increase the video frame's contrast to help with matching

    Returns:
    tuple:  (
                result: scaled thumbnail of the processed frame,
                timestamp: timestamp of the processed frame in milliseconds or -1,
                bad_frame: whether or not the frame was bad or corrupt,
                match count in the frame
            )
    '''
    
    #video.set(cv2.CAP_PROP_POS_FRAMES, 10) # Seek to frame 10
    timestamp = -1
    bad_frame = (None, timestamp, True, 0)
    success, frame = video.read()
    if not success:
        # Done with video, probably
        return None, timestamp, False, 0
    
    if not frame.any():
        print('Bad frame')
        return bad_frame

    frame_number = video.get(cv2.CAP_PROP_POS_FRAMES)
    
    #rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Increase contrast
    if boost_contrast:
        contrast = 4.0
        brightness = 0
        brightness += int(round(255 * (1 - contrast) / 2))
        frame = cv2.addWeighted(frame, contrast, frame, 0, brightness)

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    height, width = image.shape
    if height <= 0 or width <= 0:
        # Discard bad frame
        print('Bad frame')
        return bad_frame

    # Generate frame desciptors
    orb = cv2.ORB_create(nfeatures=ORB_NFEATURES)
    keypoints, descriptors = orb.detectAndCompute(image, None)

    if descriptors is None: # This is absolutely idiotic syntax
        # Discard frame with no descriptors (this can be blank or corrupt frames)
        return bad_frame

    try:
        matches = matcher.knnMatch(source_descriptors, descriptors, k=2)
    except:
        return bad_frame

    good_matches = []
    for match in matches:
        # A match object has two points, but can have just one for some reason
        if len(match) < 2:
            continue
        m, n = match
        if m.distance < MATCH_FILTER_THRESHOLD * n.distance:
            good_matches.append(m)

    print('Matches for frame {}: {}'.format(int(frame_number), len(good_matches)))

    if len(good_matches) > (len(source_descriptors) * (match_threshold / 100)):
        # Possible match, so get timestamp
        timestamp = video.get(cv2.CAP_PROP_POS_MSEC)

    qImg = QImage(image.data, width, height, width, QImage.Format_Grayscale8)
    return QPixmap(qImg).scaled(scaledWidth, \
                                scaledHeight, \
                                QtCore.Qt.KeepAspectRatio, \
                                QtCore.Qt.FastTransformation), \
                                timestamp, \
                                False, \
                                len(good_matches)

def start_processing():
    '''
    Creates the asyncio tasks for processing the files in the file list or cancels the existing tasks
    '''

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
        # Clear out results table
        results_ui.resultsTable.setRowCount(0)
        ResultsWindow.setWindowTitle('{} - Results'.format(APP_TITLE))

        global file_list
        file_list = ui.fieldVideo.text().split(';')

        ui.progressBarFiles.setValue(0)
        ui.progressBarFiles.setRange(0, len(file_list))

        for index, item in enumerate(file_list):
            task = asyncio.ensure_future(scan_video(index, asyncio_semaphore))
            task.add_done_callback(processing_complete)

def set_processing_mode(processing):
    '''
    Updates the UI based on whether or not the app is processing

    Parameters:
    processing (bool): Whether or not the app is processing
    '''

    if processing:
        ui.btnStartScan.setText("Cancel")
    else:
        ui.btnStartScan.setText("Scan")

    ui.progressBar.setTextVisible(processing)
    ui.progressBarFiles.setTextVisible(processing)
    ui.btnOpenInputImage.setEnabled(not processing)
    ui.btnOpenVideo.setEnabled(not processing)
    ui.sliderMatchThresh.setEnabled(not processing)
    ui.checkBoostContrast.setEnabled(not processing)

    if not processing:
        ui.labelFileProgress.setText('')

def match_thresh_changed():
    '''
    Handler for when the match thresholder slider changes. Updates its label.
    '''

    global match_threshold
    match_threshold = ui.sliderMatchThresh.value()
    ui.labelMatchThresh.setText("{}%".format(match_threshold))

def log(message):
    '''
    Helper for adding a timestamp to the front-facing logger
    '''

    ui.textLog.append("[{}] {}".format(datetime.now().strftime("%H:%M:%S.%f"), message))

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_DisableWindowContextHelpButton)
app = QtWidgets.QApplication(sys.argv)
loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)
asyncio.events._set_running_loop(loop)
asyncio_semaphore = asyncio.Semaphore(MAX_BATCH_SIZE)

MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)

ResultsWindow = QtWidgets.QDialog(MainWindow)
results_ui = Ui_ResultsWindow()
results_ui.setupUi(ResultsWindow)
results_ui.resultsTable.setHorizontalHeaderLabels(['File', 'Timestamp', 'Confidence', 'Thumbnail'])

# Defaults
ui.sliderMatchThresh.setSliderPosition(match_threshold)
ui.labelMatchThresh.setText("{}%".format(match_threshold))

# EVENTS
ui.btnOpenInputImage.clicked.connect(open_image_path)
ui.btnOpenVideo.clicked.connect(open_video_path)
ui.btnStartScan.clicked.connect(start_processing)
ui.btnResults.clicked.connect(lambda: ResultsWindow.show())
ui.sliderMatchThresh.valueChanged.connect(match_thresh_changed)

MainWindow.setWindowTitle(WINDOW_TITLE)
MainWindow.show()

with loop:
    loop.run_forever()