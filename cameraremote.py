#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from io import BytesIO
import logging
# import os
from PyQt5 import QtCore, QtGui, QtWidgets
from quamash import QEventLoop
import sys

from cameraremoteapi import CameraRemoteApi  # , CameraRemoteApiException
from cameraremotecontrol import CameraRemoteControl
from utils import upper_first_letter

# from utils import debug_trace


class CameraRemote(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        # --- Tabs
        self.__TABS = ["exposure", "flash", "focus", "movie", "shoot", "sound"]

        # --- Controls
        self.__CONTROLS = {
            "exposureMode": {
                "tab": "exposure",
                "widgets": "label-combo",
                "position": (0, 0),
                "callback": self.__current_candidates_callback
            },
            "exposureCompensation": {
                "tab": "exposure",
                "widgets": "label-combo",
                "position": (0, 1),
                "type": int,
                "callback": self.__current_candidates_callback
            },
            "fNumber": {
                "tab": "exposure",
                "widgets": "label-combo",
                "position": (0, 2),
                "callback": self.__current_candidates_callback
            },
            "shutterSpeed": {
                "tab": "exposure",
                "widgets": "label-combo",
                "position": (1, 0),
                "callback": self.__current_candidates_callback
            },
            "isoSpeedRate": {
                "tab": "exposure",
                "widgets": "label-combo",
                "position": (1, 1),
                "callback": self.__current_candidates_callback
            },
            "postviewImageSize": {
                "tab": "exposure",
                "widgets": "label-combo",
                "position": (1, 2),
                "callback": self.__current_candidates_callback
            },
            "flashMode": {
                "tab": "flash",
                "widgets": "label-combo",
                "position": (0, 0),
                "callback": self.__current_candidates_callback
            },
            "focusMode": {
                "tab": "focus",
                "widgets": "label-combo",
                "position": (0, 0),
                "callback": self.__current_candidates_callback
            },
            "movieQuality": {
                "tab": "movie",
                "widgets": "label-combo",
                "position": (0, 0),
                "callback": self.__current_candidates_callback
            },
            "steadyMode": {
                "tab": "shoot",
                "widgets": "label-combo",
                "position": (0, 0),
                "callback": self.__current_candidates_callback
            },
            "viewAngle": {
                "tab": "shoot",
                "widgets": "label-combo",
                "position": (0, 1),
                "callback": self.__current_candidates_callback
            },
            "selfTimer": {
                "tab": "shoot",
                "widgets": "label-combo",
                "position": (0, 2),
                "type": int,
                "callback": self.__current_candidates_callback
            },
            "shootMode": {
                "tab": "shoot",
                "widgets": "label-combo",
                "position": (1, 0),
                "callback": self.__current_candidates_callback
            },
            "actHalfPressShutter": {
                "tab": "shoot",
                "widgets": "button",
                "function-as-name": True,
                "position": (1, 1),
            },
            "cancelHalfPressShutter": {
                "tab": "shoot",
                "widgets": "button",
                "function-as-name": True,
                "position": (1, 2),
            },
            "actTakePicture": {
                "tab": "shoot",
                "widgets": "button",
                "function-as-name": True,
                "position": (2, 0),
                "submit-callback": self.__take_picture_function_callback
            },
            "beepMode": {
                "tab": "sound",
                "widgets": "label-combo",
                "position": (0, 0),
                "callback": self.__current_candidates_callback
            },
        }

        self.__init_ui()
        self.__camera_remote_api = None
        self.__camera_remote_control = CameraRemoteControl(
            "ILCE",
            self.__device_available_callback
        )

        self.__closing_actions = False

        # lock for downloading only one picture at a time. this prevents from
        # sharing the progress bar and the pixmap which are unique. this way a
        # picture will be shown while the next is beeing downloded...
        self.__download_lock = asyncio.Lock()

    def __take_picture_callback(self, event, data):
        urls = data["takePictureUrl"]
        for url in urls:
            asyncio.ensure_future(self.__download_picture(url))

    def __update_status_callback(self, event, data):
        self.__status_label.setText(data["cameraStatus"])

    def __current_candidates_callback(self, event, data):
        label = self.__CONTROLS[event]["Label"]
        combo_box = self.__CONTROLS[event]["ComboBox"]
        current_value = data["Current"]
        label.setText(str(current_value))
        combo_box.clear()
        for choice in data["Candidates"]:
            combo_box.addItem(str(choice))

    async def __device_available_callback(self, device_name, endpoint_url):
        logger.debug("device %s is connected" % (device_name,))

        camera_remote_api = CameraRemoteApi(endpoint_url, loop)
        self.__camera_remote_api = camera_remote_api

        events_watcher = await camera_remote_api.initial_checks()
        callbacks = {}
        for key, value in self.__CONTROLS.items():
            if "callback" in value:
                callbacks[key] = value["callback"]
        callbacks.update({"cameraStatus": self.__update_status_callback})
        callbacks.update({"takePicture": self.__take_picture_callback})
        events_watcher.register_events(callbacks)
        self.__camera_remote_api.start_event_watcher()

        await camera_remote_api.startRecMode()

    async def __download_picture(self, url):
        with (await self.__download_lock):
            with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        if resp.headers["CONTENT-TYPE"] == "image/jpeg":
                            content_length = int(resp.headers["CONTENT-LENGTH"])
                            downloaded = 0
                            with BytesIO() as fd:
                                while True:
                                    chunk = await resp.content.read(1024)
                                    if not chunk:
                                        break
                                    downloaded += len(chunk)
                                    percent = int(downloaded * 100 / content_length)
                                    self.__download_progress_bar.setValue(percent)
                                    fd.write(chunk)
                                data = fd.getvalue()
                            self.__download_progress_bar.reset()
                            pixmap = QtGui.QPixmap()
                            pixmap.loadFromData(QtCore.QByteArray(data))
                            scaled_pixmap = pixmap.scaled(
                                self.__picture_view_label.size(),
                                QtCore.Qt.KeepAspectRatio,
                                QtCore.Qt.SmoothTransformation
                            )
                            self.__picture_view_label.setPixmap(scaled_pixmap)

    def __take_picture_function_callback(self, f):
        result = f.result()
        url = result[0][0]
        asyncio.ensure_future(self.__download_picture(url))

    def __submit(self):
        if self.__camera_remote_api is None:
            return

        sender = self.sender()
        object_name = str(sender.objectName())

        control = self.__CONTROLS[object_name]
        function_as_name = control.get("function-as-name", False)
        if function_as_name:
            function_callback = control.get("submit-callback")
            function_name = object_name
            kwargs = {}
        else:
            function_callback = None
            value = sender.currentText()
            type_ = self.__CONTROLS[object_name].get("type", str)
            value = type_(value)
            kwargs = {object_name: value}
            function_name = "set" + upper_first_letter(object_name)

        logger.info("set %s parameter to %s" % (function_name, str(kwargs)))
        function = getattr(self.__camera_remote_api, function_name)
        function_future = asyncio.ensure_future(function(**kwargs))
        if function_callback:
            function_future.add_done_callback(function_callback)

    def __init_menu_bar(self):
        menubar = self.menuBar()

        quit_action = QtWidgets.QAction("Quit", self)
        quit_action.triggered.connect(self.close)

        file_ = menubar.addMenu("File")
        file_.addAction(quit_action)

    def __init_ui(self):
        self.setWindowTitle("Remote control for Sony Cameras")
        self.__init_menu_bar()

        self.__status_label = QtWidgets.QLabel()
        self.__status_label.setAlignment(QtCore.Qt.AlignLeft)
        self.__download_progress_bar = QtWidgets.QProgressBar()
        self.__download_progress_bar.setRange(0, 100)
        self.statusBar().addPermanentWidget(self.__status_label, 1)
        self.statusBar().addPermanentWidget(self.__download_progress_bar, 1)

        # x and y coordinates on the screen, width, height
        self.setGeometry(100, 100, 1030, 800)

        # create a window and add the layout
        window = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()
        window.setLayout(layout)
        self.setCentralWidget(window)

        tabs = QtWidgets.QTabWidget()
        layout.addWidget(tabs, 0, 0)
        for tab in self.__TABS:
            widget = QtWidgets.QWidget()
            tabs.addTab(widget, tab)
            layout = QtWidgets.QGridLayout()
            widget.setLayout(layout)
            max_x = max_y = 0
            for control_name, control_value in self.__CONTROLS.items():
                if control_value["tab"] == tab:
                    hbox_layout = QtWidgets.QHBoxLayout()
                    if control_value["widgets"] == "label-combo":

                        label = QtWidgets.QLabel("")
                        combo_box = QtWidgets.QComboBox()
                        combo_box.setObjectName(control_name)
                        combo_box.activated.connect(self.__submit)

                        hbox_layout.addWidget(label)
                        hbox_layout.addWidget(combo_box)

                        control_value["Label"] = label
                        control_value["ComboBox"] = combo_box

                        group_box = QtWidgets.QGroupBox(control_name)
                    elif control_value["widgets"] == "button":
                        button = QtWidgets.QPushButton(control_name)
                        button.setObjectName(control_name)
                        button.clicked.connect(self.__submit)
                        hbox_layout.addWidget(button)

                        group_box = QtWidgets.QGroupBox()

                    group_box.setLayout(hbox_layout)
                    x, y = control_value["position"]
                    if x > max_x:
                        max_x = x
                    if y > max_y:
                        max_y = y
                    layout.addWidget(group_box, x, y)

            hbox = QtWidgets.QHBoxLayout()
            hbox.addStretch(1)
            layout.addLayout(hbox, 0, max_x + 1, 1, max_y + 1)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addStretch(1)
            layout.addLayout(vbox, max_y + 1, 0, max_x + 1, 1)

        # --- Picture view tab
        # use a layout (does not work better)
        self.__picture_view_label = QtWidgets.QLabel()
        self.__picture_view_label.setAlignment(QtCore.Qt.AlignTop)
        self.__picture_view_label.setMargin(0)
        picture_view_layout = QtWidgets.QHBoxLayout()
        picture_view_layout.addWidget(self.__picture_view_label)
        picture_view_layout.setContentsMargins(0, 0, 0, 0)
        picture_view_widget = QtWidgets.QWidget()
        picture_view_widget.setLayout(picture_view_layout)
        tabs.addTab(picture_view_widget, "picture view")

        # ---Test tab
        button1 = QtWidgets.QPushButton("button1")
        button2 = QtWidgets.QPushButton("button2")
        test_layout = QtWidgets.QHBoxLayout()
        test_layout.addWidget(button1)
        test_layout.addWidget(button2)

        test_widget = QtWidgets.QWidget()
        test_widget.setLayout(test_layout)

        button1.clicked.connect(self.__button1_callback)
        button2.clicked.connect(self.__button2_callback)
        tabs.addTab(test_widget, "test")

    def __button1_callback(self):
        asyncio.ensure_future(self.__camera_remote_api.getAvailableApiList())

    def __button2_callback(self):
        asyncio.ensure_future(self.__camera_remote_api.getVersions())

    def __pre_close_callback(self, f):
        self.__closing_actions = True
        self.close()

    def closeEvent(self, event):
        if self.__closing_actions:
            self.__camera_remote_api.close()
            logger.info("finished")
        else:
            if self.__camera_remote_api is not None:
                stop_future = asyncio.ensure_future(self.__camera_remote_api.stopRecMode())
                stop_future.add_done_callback(self.__pre_close_callback)
                event.ignore()
            else:
                logger.info("finished")


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
