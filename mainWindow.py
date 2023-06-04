# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(760, 280)
        MainWindow.setMinimumSize(QtCore.QSize(760, 280))
        MainWindow.setMaximumSize(QtCore.QSize(760, 280))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(430, 0, 322, 271))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.loginBiliBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.loginBiliBtn.setObjectName("loginBiliBtn")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.loginBiliBtn)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.clipCheck = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.clipCheck.setObjectName("clipCheck")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.clipCheck)
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.broadcastCheck = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.broadcastCheck.setObjectName("broadcastCheck")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.broadcastCheck)
        self.verticalLayout.addLayout(self.formLayout_2)
        self.logText = QtWidgets.QTextBrowser(self.centralwidget)
        self.logText.setGeometry(QtCore.QRect(0, 0, 431, 280))
        self.logText.setObjectName("logText")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(590, 250, 150, 20))
        self.label_3.setObjectName("label_3")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(440, 70, 269, 194))
        self.label_5.setObjectName("label_5")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 760, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        self.loginBiliBtn.clicked.connect(MainWindow.login) # type: ignore
        self.clipCheck.clicked['bool'].connect(MainWindow.qrCodeSwitch) # type: ignore
        self.broadcastCheck.clicked['bool'].connect(MainWindow.broadcastSwitch) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "崩坏3外置扫码器 v.1.4.4-cmd"))
        self.label.setText(_translate("MainWindow", "登录B站账户"))
        self.loginBiliBtn.setText(_translate("MainWindow", "点击登录"))
        self.label_2.setText(_translate("MainWindow", "监听二维码"))
        self.clipCheck.setText(_translate("MainWindow", "当前状态:关闭"))
        self.label_4.setText(_translate("MainWindow", "发送到手机端"))
        self.broadcastCheck.setText(_translate("MainWindow", "当前状态:关闭"))
        self.logText.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.label_3.setText(_translate("MainWindow", "Powered By Hao_cen"))
        self.label_5.setText(_translate("MainWindow", "\n"
"简易使用说明：\n"
"第一次使用需要点击登录按钮登录B站账号\n"
"后续会将账号密码储存在配置文件内自动登录\n"
"请注意保护好文件安全\n"
"\n"
"然后将监听二维码勾选上\n"
"这时候在剪贴板中的二维码图片将会自动识别\n"
"可以使用键盘上的PrintScreen按键快速截图"))
