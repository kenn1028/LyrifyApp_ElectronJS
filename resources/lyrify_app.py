'''
Spotify Lyrics Player Project (June 2020)

Dependencies:
pip install pyqt5
pip install pyqt5-tools


Opening Qt Designer in console: type: "pyqt5designer"
Converting .ui to .py: type: 'pyuic5 -x file.ui -o file.py'

References:
https://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt
https://nikolak.com/pyqt-threading-tutorial/

PS.
ElectronJS : https://www.electronjs.org/docs/tutorial/first-app#installing-electron
            https://www.youtube.com/watch?v=627VBkAhKTc
Xojo : https://www.xojo.com/?utm_source=quora&utm_medium=content&utm_campaign=dev
'''

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!

#  ========================================================================================== #

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from threading import Thread
import sys
import time
import webbrowser
from data.spotify_client import SpotifyAPI
from data.lyrics_scraper import ColorCodedLyrics

#  ========================================================================================== #

'''
Notes:

> change thread approach, avoid doing .request on update functions - DONE
> reduce # of requests - DONE
> lyrics fetching not separated in the thread - DONE

> double check for error handling
> file opening existing user's profile if token.txt already exists and is run in a new system
> initial authentication code dialogue box
> build executable file, independent of console
> improve search function in lyrics fetching to reduce time complexity



Features to be added (according to priority):

> PyQtDesigner Changes - DONE
    1.) Window size
    - Resizable or fixed
> Toggle language buttons - DONE
> Profile picture button, and redirect to Spotify URL - DONE
    - needs get_profile() functions in SpotifyAPI Class
> App logo for main bar and taskbar - DONE


> Aesthetics Changes
    1.) Lyrics scroll bar - minimalist, flat - DONE(?), scrollbar background color issue
    2.) Window bar -  hide/recolor
    3.) Lyrics - font style and size
    4.) Add Green accent on buttons/UI

> Settings button
    - Light mode (?)

'''

#  ========================================================================================== #

class Ui_MainWindow(object):
    data = None
    song_name_ = None
    song_link_ = None
    artist_name_ = None
    artist_link_ = None
    song_length_ = None
    song_progress_ = None
    lyrics = None
    shown_lyrics = "native"
    profile_link = None

    def __init__(self):
        super().__init__()
        # 1 - create Worker and Thread inside the Form
        self.obj = UpdateThread()  # no parent!
        self.thread = QThread()  # no parent!

        # 2 - Connect Worker`s Signals to Form method slots to post data.
        self.obj.data.connect(self.update_player)
        self.obj.progress.connect(self.update_progress)

        # 3 - Move the Worker object to the Thread object
        self.obj.moveToThread(self.thread)

        # 4 - Connect Worker Signals to the Thread slots
        self.obj.finished.connect(self.thread.quit)

        # 5 - Connect Thread started signal to Worker operational slot method
        self.thread.started.connect(self.obj.update)

        # * - Thread finished signal will close the app if you want!
        #self.thread.finished.connect(app.exit)

        # 6 - Start the thread
        self.thread.start()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(450,600)
        MainWindow.setStyleSheet("QMainWindow {\n"
            "    background-color: rgb(24, 24, 24);\n"
            "}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("QWidget {\n"
            "    background-color: rgb(40, 40, 40);\n"
            "}")
        self.centralwidget.setObjectName("centralwidget")
        self.player_widget = QtWidgets.QWidget(self.centralwidget)
        self.player_widget.setGeometry(QtCore.QRect(0, 0, 450, 150))
        self.player_widget.setStyleSheet("QWidget {\n"
            "    background-color: rgb(24, 24, 24);\n"
            "}")
        self.player_widget.setObjectName("player_widget")


        self.song_image = QtWidgets.QWidget(self.player_widget)
        self.song_image.setGeometry(QtCore.QRect(0, 0, 150, 150))
        self.song_image.setAutoFillBackground(False)
        self.song_image.setStyleSheet("QFrame{\n"
            "    background-color: rgb(154, 154, 154);\n"
            "}")
        self.song_image.setObjectName("song_image")


        self.label_3 = QtWidgets.QLabel(self.song_image)
        self.label_3.setGeometry(QtCore.QRect(0, 0, 150, 150))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap("data/song_cover.jpg"))
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")


        self.song_length = QtWidgets.QLabel(self.player_widget)
        self.song_length.setGeometry(QtCore.QRect(365, 120, 55, 16))
        font = QtGui.QFont()
        font.setFamily("Proxima Nova Rg")
        font.setPointSize(7)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.song_length.setFont(font)
        self.song_length.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.song_length.setStyleSheet("QLabel{\n"
            "    color: rgb(179, 179, 179);\n"
            "}")
        self.song_length.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.song_length.setObjectName("song_length")
        self.song_progress = QtWidgets.QLabel(self.player_widget)
        self.song_progress.setGeometry(QtCore.QRect(170, 120, 55, 16))
        font = QtGui.QFont()
        font.setFamily("Proxima Nova Rg")
        font.setPointSize(7)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.song_progress.setFont(font)
        self.song_progress.setStyleSheet("QLabel{\n"
            "    color: rgb(179, 179, 179);\n"
            "}\n"
            "")
        self.song_progress.setObjectName("song_progress")


        self.song_name = QtWidgets.QLabel(self.player_widget)
        self.song_name.setGeometry(QtCore.QRect(170, 40, 231, 21))
        font = QtGui.QFont()
        font.setFamily("Proxima Nova Alt Rg")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.song_name.setFont(font)
        self.song_name.setStyleSheet("QLabel{\n"
            "    color: white;\n"
            "}")
        self.song_name.setOpenExternalLinks(True)
        self.song_name.setObjectName("song_name")


        self.artist_name = QtWidgets.QLabel(self.player_widget)
        self.artist_name.setGeometry(QtCore.QRect(170, 70, 231, 20))
        font = QtGui.QFont()
        font.setFamily("Proxima Nova Rg")
        font.setPointSize(9)
        self.artist_name.setFont(font)
        self.artist_name.setStyleSheet("QLabel{\n"
            "    color: rgb(179, 179, 179);\n"
            "}")
        self.artist_name.setOpenExternalLinks(True)
        self.artist_name.setObjectName("artist_name")


        self.song_progressBar = QtWidgets.QProgressBar(self.player_widget)
        self.song_progressBar.setGeometry(QtCore.QRect(170, 110, 250, 6))
        self.song_progressBar.setStyleSheet("QProgressBar:horizontal {\n"
            "border-radius: 2px;\n"
            "background: rgb(64, 64, 64);\n"
            "}\n"
            "QProgressBar::chunk:horizontal {\n"
            "border-radius: 2px;\n"
            "background: rgb(179, 179, 179);\n"
            "}")
        self.song_progressBar.setProperty("value", 24)
        self.song_progressBar.setTextVisible(False)
        self.song_progressBar.setObjectName("song_progressBar")


        self.lyrics_widget = QtWidgets.QWidget(self.centralwidget)
        self.lyrics_widget.setGeometry(QtCore.QRect(0, 150, 450, 450))
        self.lyrics_widget.setObjectName("lyrics_widget")


        self.user_profile = QtWidgets.QPushButton(self.player_widget)
        self.user_profile.setIcon(QtGui.QIcon("data/profile_picture.jpg"))
        self.user_profile.setIconSize(QtCore.QSize(40, 40))
        self.user_profile.setGeometry(QtCore.QRect(405, 10, 40, 40))
        self.user_profile.setMask(QtGui.QRegion(self.user_profile.rect(), QtGui.QRegion.Ellipse))
        self.user_profile.setMouseTracking(True)
        self.user_profile.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(24, 24, 24);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(60, 60, 60);\n"
            "    color: white;\n"
            "    border: 6px white;\n"
            " }")
        self.user_profile.setObjectName("user_profile")
        self.user_profile.clicked.connect(self.profile_redirect)

        self.settings = QtWidgets.QToolButton(self.player_widget)
        self.settings.setGeometry(QtCore.QRect(410, 60, 40, 40))
        self.settings.setStyleSheet("QToolButton{\n"
            "    background-color: rgb(24, 24, 24);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QToolButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QToolButton:hover {\n"
            "    background-color: rgb(60, 60, 60);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")
        self.settings.setObjectName("settings")


        self.nativeButton = QtWidgets.QPushButton(self.lyrics_widget)
        self.nativeButton.setGeometry(QtCore.QRect(0, 410, 150, 40))
        font = QtGui.QFont()
        font.setFamily("Proxima Nova Rg")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.nativeButton.setFont(font)
        self.nativeButton.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(35, 35, 35);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(60, 60, 60);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")
        self.nativeButton.setObjectName("nativeButton")
        self.nativeButton.clicked.connect(self.native_lyrics)

        self.romajiButton = QtWidgets.QPushButton(self.lyrics_widget)
        self.romajiButton.setGeometry(QtCore.QRect(150, 410, 150, 40))
        font = QtGui.QFont()
        font.setFamily("Proxima Nova Rg")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.romajiButton.setFont(font)
        self.romajiButton.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(40, 40, 40);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(60, 60, 60);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")
        self.romajiButton.setObjectName("romajiButton")
        self.romajiButton.clicked.connect(self.romaji_lyrics)


        self.englishButton = QtWidgets.QPushButton(self.lyrics_widget)
        self.englishButton.setGeometry(QtCore.QRect(300, 410, 150, 40))
        font = QtGui.QFont()
        font.setFamily("Proxima Nova Rg")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.englishButton.setFont(font)
        self.englishButton.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(40, 40, 40);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(60, 60, 60);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")
        self.englishButton.setObjectName("englishButton")
        self.englishButton.clicked.connect(self.english_lyrics)


        self.textEdit = QtWidgets.QTextEdit(self.lyrics_widget)
        self.textEdit.setGeometry(QtCore.QRect(0, -5, 450, 415))
        font = QtGui.QFont()
        font.setKerning(True)
        self.textEdit.setFont(font)
        self.textEdit.setMouseTracking(False)
        self.textEdit.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.textEdit.setStyleSheet("""
            QTextEdit {
                background: rgb(40, 40, 40);
                border: 1px solid rgb(35, 35, 35);
                }

            QAbstractScrollArea:vertical {
                width: 45px;
                margin: 5px 0 5px 0;
                }

            QAbstractScrollArea::handle:vertical {
            min-height: 20px;
            }
        """)
        self.textEdit.verticalScrollBar().setStyleSheet("""
            QScrollBar:horizontal {
                min-width: 240px;
                height: 13px;
            }

            QScrollBar:vertical {
                min-height: 240px;
                width: 13px;
                background-color: rgb(45, 45, 45);
                border-radius: 5px;
            }

            QScrollBar::groove {
                background: #333333;
                border-radius: 5px;
            }

            QScrollBar::handle {
                background: rgb(60, 60, 60);
                border-radius: 5px;
            }

            QScrollBar::handle:horizontal {
                width: 25px;
            }

            QScrollBar::handle:vertical {
                height: 25px;
            }
            
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }

            QScrollBar::add-line:vertical {
                border: none;
                background: none;
            }

            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            """)

        self.textEdit.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.textEdit.setLineWidth(0)
        self.textEdit.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.textEdit.setAutoFormatting(QtWidgets.QTextEdit.AutoNone)
        self.textEdit.setTabChangesFocus(False)
        self.textEdit.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.textEdit.setReadOnly(True)
        self.textEdit.setOverwriteMode(True)
        self.textEdit.setObjectName("textEdit")


        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "LyrifyApp"))
        MainWindow.setWindowIcon(QtGui.QIcon('ui/lyrify_ico.png'))
        self.artist_name.setText(_translate("MainWindow", "artist_name"))
        self.song_length.setText(_translate("MainWindow", "song_length"))
        self.song_progress.setText(_translate("MainWindow", "song_progress"))
        self.settings.setText(_translate("MainWindow", "..."))
        self.song_name.setText(_translate("MainWindow", "song_name"))
        self.nativeButton.setText(_translate("MainWindow", "Native"))
        self.romajiButton.setText(_translate("MainWindow", "Romanized"))
        self.englishButton.setText(_translate("MainWindow", "English"))
        self.textEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
            f"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>"))

    def update_player(self, data):
        _translate = QtCore.QCoreApplication.translate

        song_name = data["song_name"]

        self.song_link = ''.join(data["song_link"])  #converts Tuple to String
        self.artist_link = ''.join(data["artist_link"])
        self.profile_link = ''.join(data["profile_link"])

        self.artist_name.setText(f"<a href = '{self.artist_link}' style='text-decoration:none'><font color=#b3b3b3> {data['artist_name']} </font></a>")
        self.song_length.setText(data["song_length"])
        self.song_name.setText(f"<a href = '{self.song_link}' style='text-decoration:none'><font color=white>{data['song_name']}</a>")
        self.label_3.setPixmap(QtGui.QPixmap("data/song_cover.jpg"))
        self.user_profile.setIcon(QtGui.QIcon("data/profile_picture.jpg"))
        
        if self.song_name_ != song_name:
            try:
                self.lyrics = data["lyrics"]
                lyrics = self.lyrics[self.shown_lyrics]
                lyrics = lyrics.replace('<td>', '').replace('</td>', '')

                self.textEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
                f"<div class='centeralign'><span align=\"center\" style=\" color: '#c7c7c7'; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><center><br>{lyrics}<br></center></span></div></body></html>"))
                self.song_name_ = song_name
            except:
                pass
            # time.sleep(1)

    def update_progress(self, progress):
        song_progress = progress["song_progress"]
        song_length = progress["song_length"]
        value = int((float(song_progress.replace(':', '.'))/float(song_length.replace(':', '.'))) * 100)
        self.song_progress.setText(f"{song_progress}")
        self.song_progressBar.setProperty("value", value)

# ==================================== Button Functions ===================================== #

    def romaji_lyrics(self):
        _translate = QtCore.QCoreApplication.translate

        self.shown_lyrics = "romanization"

        self.nativeButton.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(40, 40, 40);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(50, 50, 50);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")

        self.romajiButton.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(35, 35, 35);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(50, 50, 50);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")

        self.englishButton.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(40, 40, 40);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(50, 50, 50);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")

        lyrics = str(self.lyrics["romanization"])
        lyrics = lyrics.replace('<td>', '').replace('</td>', '')

        self.textEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
        "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
        f"<div class='centeralign'><span align=\"center\" style=\" color: '#c7c7c7'; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><center><br>{lyrics}<br></center></span></div></body></html>"))

# ==================================== Button Functions ===================================== #

    def native_lyrics(self):
        _translate = QtCore.QCoreApplication.translate

        self.shown_lyrics = "native"

        self.nativeButton.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(35, 35, 35);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(50, 50, 50);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")

        self.romajiButton.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(40, 40, 40);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(50, 50, 50);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")

        self.englishButton.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(40, 40, 40);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(50, 50, 50);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")

        lyrics = str(self.lyrics["native"])
        lyrics = lyrics.replace('<td>', '').replace('</td>', '')

        self.textEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
        "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
        f"<div class='centeralign'><span align=\"center\" style=\" color: '#c7c7c7'; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><center><br>{lyrics}<br></center></span></div></body></html>"))

# ==================================== Button Functions ===================================== #

    def english_lyrics(self):
        _translate = QtCore.QCoreApplication.translate

        self.shown_lyrics = "english"

        self.nativeButton.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(40, 40, 40);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(50, 50, 50);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")

        self.romajiButton.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(40, 40, 40);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(50, 50, 50);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")

        self.englishButton.setStyleSheet("QPushButton{\n"
            "    background-color: rgb(35, 35, 35);\n"
            "    color: white;\n"
            "    border: none;\n"
            "}\n"
            " QPushButton:pressed {\n"
            "    background-color: rgb(20, 20, 20);     \n"
            "    color: white;\n"
            "    border: none;\n"
            " }\n"
            " QPushButton:hover {\n"
            "    background-color: rgb(50, 50, 50);\n"
            "    color: white;\n"
            "    border: none;\n"
            " }")

        lyrics = str(self.lyrics["english"])
        lyrics = lyrics.replace('<td>', '').replace('</td>', '')

        self.textEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
        "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
        f"<div class='centeralign'><span align=\"center\" style=\" color: '#c7c7c7'; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><center><br>{lyrics}<br></center></span></div></body></html>"))

# ==================================== Button Functions ===================================== #

    def profile_redirect(self):
        webbrowser.open(self.profile_link)

# ==================================== Worker Class ===================================== #

class UpdateThread(QObject):
    data = pyqtSignal(dict)
    progress = pyqtSignal(dict)
    finished = pyqtSignal()

    @pyqtSlot()
    def update(self):
        while True:
            data = spotify.get_current_song()
            profile_data = spotify.get_current_profile()

            song_name = data["song_name"]
            artist_name = data["artist"]

            self.progress.emit({
                "song_name" : data["song_name"],
                "song_length" : data["song_length"],
                "song_progress" : data["song_progress"]
            })

            if ui.song_name_ != song_name:
                self.data.emit({
                    "song_name" : data["song_name"],
                    "song_link" : data["song_link"],
                    "artist_name" : data["artist"],
                    "artist_link" : data["artist_link"],
                    "song_progress" : data["song_progress"],
                    "song_length" : data["song_length"],
                    "profile_link" : profile_data,
                })
                self.data.emit({
                    "song_name" : data["song_name"],
                    "song_link" : data["song_link"],
                    "artist_name" : data["artist"],
                    "artist_link" : data["artist_link"],
                    "song_progress" : data["song_progress"],
                    "song_length" : data["song_length"],
                    "profile_link" : profile_data,
                    "lyrics" : ColorCodedLyrics(song_name = song_name, artist_name = artist_name).get_lyrics()
                })
                # time.sleep(1)

            self.finished.emit()
            # time.sleep(1)

#  ========================================================================================== #

if __name__ == "__main__":
    spotify = SpotifyAPI()

    try:
        spotify.perform_refresh()
    except:
        spotify.get_scopes()
        spotify.auth_code = input("Enter Code: ")
        spotify.perform_auth()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
