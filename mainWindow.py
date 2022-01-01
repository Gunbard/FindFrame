# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\findFrameMain.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(512, 240)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(512, 240))
        MainWindow.setMaximumSize(QtCore.QSize(512, 240))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 71, 21))
        self.label.setObjectName("label")
        self.fieldInputImage = QtWidgets.QLineEdit(self.centralwidget)
        self.fieldInputImage.setGeometry(QtCore.QRect(90, 10, 361, 20))
        self.fieldInputImage.setObjectName("fieldInputImage")
        self.btnOpenInputImage = QtWidgets.QPushButton(self.centralwidget)
        self.btnOpenInputImage.setGeometry(QtCore.QRect(460, 10, 41, 21))
        self.btnOpenInputImage.setObjectName("btnOpenInputImage")
        self.imageInput = QtWidgets.QLabel(self.centralwidget)
        self.imageInput.setGeometry(QtCore.QRect(250, 110, 121, 91))
        self.imageInput.setFrameShape(QtWidgets.QFrame.Panel)
        self.imageInput.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.imageInput.setText("")
        self.imageInput.setScaledContents(False)
        self.imageInput.setObjectName("imageInput")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 71, 21))
        self.label_2.setObjectName("label_2")
        self.fieldVideo = QtWidgets.QLineEdit(self.centralwidget)
        self.fieldVideo.setGeometry(QtCore.QRect(90, 40, 361, 20))
        self.fieldVideo.setObjectName("fieldVideo")
        self.btnOpenVideo = QtWidgets.QPushButton(self.centralwidget)
        self.btnOpenVideo.setGeometry(QtCore.QRect(460, 40, 41, 23))
        self.btnOpenVideo.setObjectName("btnOpenVideo")
        self.textLog = QtWidgets.QTextEdit(self.centralwidget)
        self.textLog.setGeometry(QtCore.QRect(10, 110, 231, 91))
        self.textLog.setFrameShape(QtWidgets.QFrame.Panel)
        self.textLog.setUndoRedoEnabled(False)
        self.textLog.setReadOnly(True)
        self.textLog.setObjectName("textLog")
        self.btnStartScan = QtWidgets.QPushButton(self.centralwidget)
        self.btnStartScan.setGeometry(QtCore.QRect(180, 70, 161, 31))
        self.btnStartScan.setObjectName("btnStartScan")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(10, 210, 491, 20))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.imageVideoFrame = QtWidgets.QLabel(self.centralwidget)
        self.imageVideoFrame.setGeometry(QtCore.QRect(380, 110, 121, 91))
        self.imageVideoFrame.setFrameShape(QtWidgets.QFrame.Panel)
        self.imageVideoFrame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.imageVideoFrame.setText("")
        self.imageVideoFrame.setScaledContents(False)
        self.imageVideoFrame.setObjectName("imageVideoFrame")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FindFrame"))
        self.label.setText(_translate("MainWindow", "Input image:"))
        self.btnOpenInputImage.setText(_translate("MainWindow", "..."))
        self.label_2.setText(_translate("MainWindow", "Video:"))
        self.btnOpenVideo.setText(_translate("MainWindow", "..."))
        self.btnStartScan.setText(_translate("MainWindow", "Scan Video"))