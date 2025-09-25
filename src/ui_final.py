# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6 import QtCore, QtWidgets, QtGui
#import logo


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(720, 480)  # 저해상도 고정 (원하면 resize로 바꿔도 됨)

        # --- central widget & root layout ---
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        root_v = QtWidgets.QVBoxLayout(self.centralwidget)
        root_v.setContentsMargins(8, 8, 8, 8)
        root_v.setSpacing(8)

        # ================= 상단: 좌(카메라) + 우(텍스트/버튼/리스트) =================
        top_h = QtWidgets.QHBoxLayout()
        top_h.setSpacing(8)
        root_v.addLayout(top_h, 1)

        # (좌) 카메라 블록
        left_v = QtWidgets.QVBoxLayout()
        self.label_camera_title = QtWidgets.QLabel("Camera View", self.centralwidget)
        self.camera_view = QtWidgets.QLabel(self.centralwidget)
        self.camera_view.setObjectName("camera_view")
        self.camera_view.setMinimumSize(QtCore.QSize(320, 240))  # 4:3 최소 확보
        self.camera_view.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_view.setStyleSheet("background:#111; color:#bbb;")
        self.camera_view.setText("No Signal")
        left_v.addWidget(self.label_camera_title)
        left_v.addWidget(self.camera_view, 1)
        top_h.addLayout(left_v, 1)

        # (우) 현재 텍스트 + 버튼 두 개 + 복용중 리스트
        right_v = QtWidgets.QVBoxLayout()
        self.label_current_text = QtWidgets.QLabel("Current Text", self.centralwidget)
        self.ocr_result_label = QtWidgets.QLabel("Pill name will be displayed here.", self.centralwidget)
        self.ocr_result_label.setObjectName("ocr_result_label")
        self.ocr_result_label.setWordWrap(True)

        btn_h = QtWidgets.QHBoxLayout()
        self.add_medicine_button = QtWidgets.QPushButton("ADD", self.centralwidget)
        self.add_medicine_button.setObjectName("add_medicine_button")
        self.quit_button = QtWidgets.QPushButton("QUIT", self.centralwidget)
        self.quit_button.setObjectName("quit_button")
        btn_h.addWidget(self.add_medicine_button)
        btn_h.addWidget(self.quit_button)

        self.label_taking = QtWidgets.QLabel("Currently Taking", self.centralwidget)
        self.my_medicines_list_view = QtWidgets.QListView(self.centralwidget)
        self.my_medicines_list_view.setObjectName("my_medicines_list_view")

        right_v.addWidget(self.label_current_text)
        right_v.addWidget(self.ocr_result_label)
        right_v.addLayout(btn_h)
        right_v.addWidget(self.label_taking)
        right_v.addWidget(self.my_medicines_list_view, 1)
        top_h.addLayout(right_v, 1)

        # ================= 하단: DUR 검색 결과(스크롤 + 테이블) =================
        self.label_dur = QtWidgets.QLabel("DUR Search Results", self.centralwidget)
        root_v.addWidget(self.label_dur)

        self.dur_data_scroll_area = QtWidgets.QScrollArea(self.centralwidget)
        self.dur_data_scroll_area.setObjectName("dur_data_scroll_area")
        self.dur_data_scroll_area.setWidgetResizable(True)

        scroll_w = QtWidgets.QWidget()
        sv_v = QtWidgets.QVBoxLayout(scroll_w)

        header_h = QtWidgets.QHBoxLayout()
        header_h.addWidget(QtWidgets.QLabel("Ingredient", scroll_w))
        header_h.addWidget(QtWidgets.QLabel("Side Effects", scroll_w))
        sv_v.addLayout(header_h)

        self.dur_table_view = QtWidgets.QTableView(scroll_w)
        self.dur_table_view.setObjectName("dur_table_view")
        # 헤더 폭 자동 분배
        header = self.dur_table_view.horizontalHeader()
        header.setStretchLastSection(True)
        try:
            from PySide6.QtWidgets import QHeaderView
        except Exception:
            from PyQt5.QtWidgets import QHeaderView  # PyQt5 호환
        header.setSectionResizeMode(QHeaderView.Stretch)

        sv_v.addWidget(self.dur_table_view)
        self.dur_data_scroll_area.setWidget(scroll_w)

        root_v.addWidget(self.dur_data_scroll_area, 1)

        # --- menubar / statusbar (있으면 유지) ---
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Medicine Interaction Checker", None))
        self.quit_button.setText(QCoreApplication.translate("MainWindow", u"QUIT", None))
        self.add_medicine_button.setText(QCoreApplication.translate("MainWindow", u"ADD", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Ingredient", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Side Effects", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.ocr_result_label.setText(QCoreApplication.translate("MainWindow", u"Pill name will be displayed here.", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Current Text", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Camera View", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"DUR Search Results", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Currently Taking", None))
        self.camera_view.setText("")
        self.label_8.setText("")
        self.menuMedicine_Manager.setTitle(QCoreApplication.translate("MainWindow", u"Medicine Manager", None))
    # retranslateUi

