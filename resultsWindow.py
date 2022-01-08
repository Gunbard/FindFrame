# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\results.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ResultsWindow(object):
    def setupUi(self, ResultsWindow):
        ResultsWindow.setObjectName("ResultsWindow")
        ResultsWindow.setWindowModality(QtCore.Qt.NonModal)
        ResultsWindow.resize(540, 360)
        ResultsWindow.setModal(False)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ResultsWindow)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.resultsTable = QtWidgets.QTableWidget(ResultsWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resultsTable.sizePolicy().hasHeightForWidth())
        self.resultsTable.setSizePolicy(sizePolicy)
        self.resultsTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.resultsTable.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.resultsTable.setCornerButtonEnabled(False)
        self.resultsTable.setRowCount(0)
        self.resultsTable.setColumnCount(4)
        self.resultsTable.setObjectName("resultsTable")
        self.resultsTable.horizontalHeader().setVisible(True)
        self.resultsTable.horizontalHeader().setDefaultSectionSize(100)
        self.resultsTable.horizontalHeader().setMinimumSectionSize(100)
        self.resultsTable.horizontalHeader().setStretchLastSection(True)
        self.resultsTable.verticalHeader().setVisible(False)
        self.resultsTable.verticalHeader().setDefaultSectionSize(100)
        self.resultsTable.verticalHeader().setStretchLastSection(False)
        self.verticalLayout_2.addWidget(self.resultsTable)
        self.pushButton = QtWidgets.QPushButton(ResultsWindow)
        self.pushButton.setMinimumSize(QtCore.QSize(0, 32))
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_2.addWidget(self.pushButton)

        self.retranslateUi(ResultsWindow)
        self.pushButton.clicked.connect(ResultsWindow.accept)
        QtCore.QMetaObject.connectSlotsByName(ResultsWindow)

    def retranslateUi(self, ResultsWindow):
        _translate = QtCore.QCoreApplication.translate
        ResultsWindow.setWindowTitle(_translate("ResultsWindow", "FindFrame - Results"))
        self.pushButton.setText(_translate("ResultsWindow", "Close"))
