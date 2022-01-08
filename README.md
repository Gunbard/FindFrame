# FindFrame
Scans through videos to find matching frames. Uses OpenCV for feature detection and PyQT 5 for UI.

##### Tested with Python 3.8.6/venv on Windows 10

### Install Dependencies
```sh
pip install -r requirements.txt
```

### (Re)compiling the UI
```sh
pyuic5 findFrameWindow.ui -o mainWindow.py
pyuic5 results.ui -o resultsWindow.py
```

### Running
```sh
python main.py
```

### Building standalone executable
```sh
pip install pyinstaller
pyinstaller --onefile --noconsole main.py
```

Built exe will be in 'dist' folder

### Scan tips
 - Increase source frame/image contrast to help with feature detection. Crop out stuff that might not be in the video. The detected features will be visible in the source frame thumbnail. The more features, the more the app has the search against. Also, making sure the aspect ratio is similar will help.
 - Start with a low match threshold and bump it up until it doesn't think every frame is a match. Keep increasing until you stop getting too many false positives.

### TODO
- [] Resizable main window
- [] Match "VU meter"
- [] Show bigger image with keypoints after clicking thumbnail
- [] Find out what the hell filetypes cv2.VideoCapture supports
- [] Expose OpenCV matcher settings
- [] Process multiple files at a time (need a UI update for this). Increasing MAX_BATCH_SIZE will work, but the UI/progress bars won't be updated correctly.
- [] Built-in source frame image processing (brightness, contrast, cropping, etc.)