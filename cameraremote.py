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


class CameraRemoteWidget:
    pass


class CurrentCandidateWidget(CameraRemoteWidget):

    def __init__(self, camera_remote, widget_name, group_caption, type_=str):
        self.camera_remote = camera_remote
        self.__widget_name = widget_name
        self.__group_caption = group_caption
        self.__type = type_

        self.__widget_label = None
        self.__widget_combo_box = None

    def get_event_callback(self):
        return self.__event_callback

    def __event_callback(self, event, data):
        current_value = data["Current"]
        self.__widget_label.setText(str(current_value))
        self.__widget_combo_box.clear()
        for choice in data["Candidates"]:
            self.__widget_combo_box.addItem(str(choice))

    def __submit(self):
        value = self.__type(self.__widget_combo_box.currentText())
        kwargs = {self.__widget_name: value}
        function_name = "set" + upper_first_letter(self.__widget_name)

        logger.info("set %s parameter to %s" % (function_name, str(kwargs)))
        function = getattr(self.camera_remote.camera_api, function_name)
        asyncio.ensure_future(function(**kwargs))

    def make_widget_group_box(self):
        hbox_layout = QtWidgets.QHBoxLayout()

        self.__widget_label = QtWidgets.QLabel("")
        self.__widget_combo_box = QtWidgets.QComboBox()
        self.__widget_combo_box.setObjectName(self.__widget_name)
        self.__widget_combo_box.activated.connect(self.__submit)

        hbox_layout.addWidget(self.__widget_label)
        hbox_layout.addWidget(self.__widget_combo_box)

        group_box = QtWidgets.QGroupBox(self.__group_caption)
        group_box.setLayout(hbox_layout)
        return group_box


class ActionWidget(CameraRemoteWidget):

    def __init__(self, camera_remote, widget_name, button_caption):
        self.camera_remote = camera_remote
        self.__widget_name = widget_name
        self.__button_caption = button_caption
        self.__widget_button = None

    def get_event_callback(self):
        return

    def __submit(self):
        function_name = self.__widget_name

        logger.info("action %s" % (function_name,))
        function = getattr(self.camera_remote.camera_api, function_name)
        function_future = asyncio.ensure_future(function())
        function_future.add_done_callback(self.submit_callback)

    def submit_callback(self, f):
        pass

    def make_widget_group_box(self):
        hbox_layout = QtWidgets.QHBoxLayout()
        button = QtWidgets.QPushButton(self.__button_caption)
        button.setObjectName(self.__widget_name)
        button.clicked.connect(self.__submit)
        hbox_layout.addWidget(button)
        group_box = QtWidgets.QGroupBox()

        group_box.setLayout(hbox_layout)
        return group_box


class TakePictureWidget(ActionWidget):

    def submit_callback(self, f):
        result = f.result()
        url = result[0][0]
        asyncio.ensure_future(self.camera_remote.download_picture(url))


class CameraRemote(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        # --- Tabs
        self.__TABS = ["exposure", "flash", "focus", "movie", "shoot", "sound"]

        # --- Controls
        self.__WIDGETS = [
            {
                "name": "exposureMode",
                "tab": "exposure",
                "position": (0, 0),
                "widget": CurrentCandidateWidget(self, "exposureMode", "Exposure mode")
            },
            {
                "name": "exposureCompensation",
                "tab": "exposure",
                "position": (0, 1),
                "widget": CurrentCandidateWidget(self,
                                                 "exposureCompensation",
                                                 "Exposure compensation",
                                                 type_=int)
            },
            {
                "name": "fNumber",
                "tab": "exposure",
                "position": (0, 2),
                "widget": CurrentCandidateWidget(self, "fNumber", "F Number")
            },
            {
                "name": "shutterSpeed",
                "tab": "exposure",
                "position": (1, 0),
                "widget": CurrentCandidateWidget(self, "shutterSpeed", "Shutter Speed")
            },
            {
                "name": "isoSpeedRate",
                "tab": "exposure",
                "position": (1, 1),
                "widget": CurrentCandidateWidget(self, "isoSpeedRate", "Iso speed rate")
            },
            {
                "name": "flashMode",
                "tab": "flash",
                "position": (0, 0),
                "widget": CurrentCandidateWidget(self, "flashMode", "Flash mode")
            },
            {
                "name": "focusMode",
                "tab": "focus",
                "position": (0, 0),
                "widget": CurrentCandidateWidget(self, "focusMode", "Focus mode")
            },
            {
                "name": "movieQuality",
                "tab": "movie",
                "position": (0, 0),
                "widget": CurrentCandidateWidget(self, "movieQuality", "Movie Quality")
            },
            {
                "name": "postviewImageSize",
                "tab": "shoot",
                "position": (0, 0),
                "widget": CurrentCandidateWidget(self, "postviewImageSize", "Postview image size")
            },
            {
                "name": "steadyMode",
                "tab": "shoot",
                "position": (0, 1),
                "widget": CurrentCandidateWidget(self, "steadyMode", "Steady mode")
            },
            {
                "name": "viewAngle",
                "tab": "shoot",
                "position": (0, 2),
                "widget": CurrentCandidateWidget(self, "viewAngle", "View angle")
            },
            {
                "name": "selfTimer",
                "tab": "shoot",
                "position": (1, 0),
                "widget": CurrentCandidateWidget(self, "selfTimer", "Self timer", type_=int)
            },
            {
                "name": "shootMode",
                "tab": "shoot",
                "position": (1, 1),
                "widget": CurrentCandidateWidget(self, "shootMode", "Shoot mode")
            },
            {
                "name": "actHalfPressShutter",
                "tab": "shoot",
                "position": (2, 0),
                "widget": ActionWidget(self, "actHalfPressShutter", "Half press shutter")
            },
            {
                "name": "cancelHalfPressShutter",
                "tab": "shoot",
                "position": (2, 1),
                "widget": ActionWidget(self, "cancelHalfPressShutter", "Cancel half press shutter")
            },
            {
                "name": "actTakePicture",
                "tab": "shoot",
                "position": (2, 2),
                "widget": TakePictureWidget(self, "actTakePicture", "Take picture")
            },
            {
                "name": "beepMode",
                "tab": "sound",
                "position": (0, 0),
                "widget": CurrentCandidateWidget(self, "beepMode", "Beep mode")
            },
        ]

        self.__init_ui()
        self.camera_api = None
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
            asyncio.ensure_future(self.download_picture(url))

    def __update_status_callback(self, event, data):
        self.__status_label.setText(data["cameraStatus"])

    async def __device_available_callback(self, device_name, endpoint_url):
        logger.debug("device %s is connected" % (device_name,))

        camera_api = CameraRemoteApi(endpoint_url, loop)
        self.camera_api = camera_api

        events_watcher = await camera_api.initial_checks()
        callbacks = {}
        for widget in self.__WIDGETS:
            callback = widget["widget"].get_event_callback()
            name = widget["name"]
            if callback is not None:
                callbacks[name] = callback
        callbacks.update({"cameraStatus": self.__update_status_callback})
        callbacks.update({"takePicture": self.__take_picture_callback})
        events_watcher.register_events(callbacks)
        events_watcher.start_event_watcher()

        await camera_api.startRecMode()

    async def download_picture(self, url):
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
            for widget in self.__WIDGETS:
                if widget["tab"] == tab:
                    group_box = widget["widget"].make_widget_group_box()

                    x, y = widget["position"]
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
        asyncio.ensure_future(self.camera_api.getAvailableApiList())

    def __button2_callback(self):
        asyncio.ensure_future(self.camera_api.getVersions())

    def __pre_close_callback(self, f):
        self.__closing_actions = True
        self.close()

    def closeEvent(self, event):
        if self.__closing_actions:
            self.camera_api.close()
            logger.info("finished")
        else:
            if self.camera_api is not None:
                stop_future = asyncio.ensure_future(self.camera_api.stopRecMode())
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
