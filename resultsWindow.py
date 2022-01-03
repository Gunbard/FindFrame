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
        ResultsWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        ResultsWindow.resize(400, 300)
        ResultsWindow.setModal(True)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ResultsWindow)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.resultsTable = QtWidgets.QTableWidget(ResultsWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resultsTable.sizePolicy().hasHeightForWidth())
        self.resultsTable.setSizePolicy(sizePolicy)
        self.resultsTable.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.resultsTable.setCornerButtonEnabled(False)
        self.resultsTable.setRowCount(0)
        self.resultsTable.setColumnCount(2)
        self.resultsTable.setObjectName("resultsTable")
        self.resultsTable.horizontalHeader().setVisible(True)
        self.resultsTable.horizontalHeader().setStretchLastSection(True)
        self.resultsTable.verticalHeader().setVisible(False)
        self.resultsTable.verticalHeader().setDefaultSectionSize(100)
        self.resultsTable.verticalHeader().setStretchLastSection(True)
        self.verticalLayout_2.addWidget(self.resultsTable)
        self.pushButton = QtWidgets.QPushButton(ResultsWindow)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_2.addWidget(self.pushButton)

        self.retranslateUi(ResultsWindow)
        self.pushButton.clicked.connect(ResultsWindow.accept)
        QtCore.QMetaObject.connectSlotsByName(ResultsWindow)

    def retranslateUi(self, ResultsWindow):
        _translate = QtCore.QCoreApplication.translate
        ResultsWindow.setWindowTitle(_translate("ResultsWindow", "FindFrame - Results"))
        self.pushButton.setText(_translate("ResultsWindow", "Close"))
