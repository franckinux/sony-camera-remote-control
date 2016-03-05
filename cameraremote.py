#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
# import os
from PyQt5 import QtGui, QtWidgets  # , QtCore
from PyQt5.QtCore import Qt
from quamash import QEventLoop  # , QThreadExecutor
import sys

from cameraremoteapi import CameraRemoteApi  # , CameraRemoteApiException
from cameraremotecontrol import CameraRemoteControl
from utils import upper_first_letter

# from utils import debug_trace


class CameraRemote(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        # --- Exposure tab
        self.__EXPOSURE = {
            "exposureCompensation": {
                "position": (0, 0),
                "type": int,
                "callback": self.__current_candidates_callback
            },
            "fNumber": {
                "position": (0, 1),
                "callback": self.__current_candidates_callback
            },
            "shutterSpeed": {
                "position": (1, 0),
                "callback": self.__current_candidates_callback
            },
            "isoSpeedRate": {
                "position": (1, 1),
                "callback": self.__current_candidates_callback
            },
        }

        self.__init_ui()
        self.__camera_remote_api = None
        self.__camera_remote_control = CameraRemoteControl(
            "ILCE",
            self.__device_available_callback
        )

    def __init_menu_bar(self):
        menubar = self.menuBar()

        quit_action = QtWidgets.QAction("Quit", self)
        quit_action.triggered.connect(self.__pre_close)

        file_ = menubar.addMenu("File")
        file_.addAction(quit_action)

    def __current_candidates_callback(self, event, data):
        label = self.__EXPOSURE[event]["Label"]
        combo_box = self.__EXPOSURE[event]["ComboBox"]
        current_value = data["Current"]
        label.setText(str(current_value))
        combo_box.clear()
        for choice in data["Candidates"]:
            combo_box.addItem(choice)

    async def __device_available_callback(self, device_name, endpoint_url):
        logger.debug("device %s is connected" % (device_name,))

        camera_remote_api = CameraRemoteApi(endpoint_url, loop)
        self.__camera_remote_api = camera_remote_api

        events_watcher = await camera_remote_api.initial_checks()
        callbacks = {key: value["callback"] for key, value in self.__EXPOSURE.items()}
        events_watcher.register_events(callbacks)
        self.__camera_remote_api.start_event_watcher()

        await camera_remote_api.startRecMode()

    def __submit(self):
        if self.__camera_remote_api is None:
            return

        sender = self.sender()
        object_name = str(sender.objectName())
        value = sender.currentText()
        logger.info("set %s parameter to %s" % (object_name, value))

        type_ = self.__EXPOSURE[object_name].get("type", str)
        value = type_(value)

        function_name = "set" + upper_first_letter(object_name)
        set_function = getattr(self.__camera_remote_api, function_name)
        kwargs = {object_name: value}
        asyncio.ensure_future(set_function(**kwargs))

    def __init_ui(self):
        layout_exposure = QtWidgets.QGridLayout()
        for exp in self.__EXPOSURE:
            label = QtWidgets.QLabel("")

            combo_box = QtWidgets.QComboBox()
            combo_box.setObjectName(exp)
            combo_box.activated.connect(self.__submit)

            hbox_layout = QtWidgets.QHBoxLayout()
            hbox_layout.addWidget(label)
            hbox_layout.addWidget(combo_box)

            gb = QtWidgets.QGroupBox(exp)
            gb.setLayout(hbox_layout)

            layout_exposure.addWidget(gb, *self.__EXPOSURE[exp]["position"])
            self.__EXPOSURE[exp]["Label"] = label
            self.__EXPOSURE[exp]["ComboBox"] = combo_box

        widget_exposure = QtWidgets.QWidget()
        widget_exposure.setLayout(layout_exposure)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        layout_exposure.addLayout(hbox, 0, 2, 2, 1)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        layout_exposure.addLayout(vbox, 2, 0, 1, 2)
#        layout_exposure.setColumnStretch(0, 1)
#        layout_exposure.setColumnStretch(1, 1)
#        layout_exposure.setColumnStretch(2, 10)
#        layout_exposure.setRowStretch(0, 1)
#        layout_exposure.setRowStretch(1, 1)
#        layout_exposure.setRowStretch(2, 10)

        # --- Focus tab

        # --- Shoot tab
        self.label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(640, 480)
        pixmap.fill(Qt.red)
        self.label.setPixmap(pixmap)

        # ---Test tab
        button_start = QtWidgets.QPushButton("start")
        button_stop = QtWidgets.QPushButton("stop")
        layout_test = QtWidgets.QHBoxLayout()
        layout_test.addWidget(button_start)
        layout_test.addWidget(button_stop)

        widget_test = QtWidgets.QWidget()
        widget_test.setLayout(layout_test)

        # button_start.clicked.connect(self.__start_action)
        # button_stop.clicked.connect(self.__stop_action)

        # ---

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(widget_exposure, "Exposure")
        tabs.addTab(self.label, "Shoot")
        tabs.addTab(widget_test, "Test")

        layout = QtWidgets.QGridLayout()
        layout.addWidget(tabs, 0, 0)

        # create a window and add the layout
        window = QtWidgets.QWidget()
        window.setLayout(layout)

        self.__init_menu_bar()

        self.setCentralWidget(window)
        self.setWindowTitle("Camera Remote")

        self.statusBar().showMessage("Ready")

        # x and y coordinates on the screen, width, height
        self.setGeometry(100, 100, 1030, 800)

    def __pre_close(self):
        if self.__camera_remote_api is not None:
            stop_future = asyncio.ensure_future(self.__camera_remote_api.stopRecMode())
            stop_future.add_done_callback(self.__pre_close_callback)

    def __pre_close_callback(self, f):
        self.close()

    def closeEvent(self, event):
        if self.__camera_remote_api is not None:
            self.__camera_remote_api.close()
        logger.info("finished")
        event.accept()


app = QtWidgets.QApplication(sys.argv)
loop = QEventLoop(app)
loop.set_debug(False)
asyncio.set_event_loop(loop)

camera_remote = CameraRemote()
camera_remote.show()

logger = logging.getLogger("cameraremote")
file_handler = logging.FileHandler(filename="cameraremote.log", mode='w')
formatter = logging.Formatter("%(levelname)-8s %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
logger.info("started")

try:
    sys.exit(app.exec_())
finally:
    loop.close()
    file_handler.close()
