#!/usr/bin/env python3

import aiohttp
import asyncio
from io import BytesIO
import logging
from PySide2 import QtCore, QtGui, QtWidgets
from qasync import QEventLoop
from qasync import asyncClose
from qasync import asyncSlot
# from asyncqt import QEventLoop
# from asyncqt import asyncClose
# from asyncqt import asyncSlot
import sys

from cameraremoteapi import CameraRemoteApi  # , CameraRemoteApiException
from cameraremotecontrol import CameraRemoteControl
from utils import upper_first_letter

# from utils import debug_trace


class CameraRemoteWidget:

    def get_event_callback(self):
        return self.event_callback

    def get_name(self):
        return self.widget_name


class CurrentCandidateWidget(CameraRemoteWidget):

    def __init__(self, camera_remote, widget_name, group_caption, type_=str):
        self.camera_remote = camera_remote
        self.widget_name = widget_name
        self.__group_caption = group_caption
        self.__type = type_

        self.__widget_label = None
        self.__widget_combo_box = None

    def event_callback(self, data):
        current_value = data["Current"]
        self.__widget_label.setText(str(current_value))
        self.__widget_combo_box.clear()
        for choice in data["Candidates"]:
            self.__widget_combo_box.addItem(str(choice))

    @asyncSlot()
    async def __submit(self):
        value = self.__type(self.__widget_combo_box.currentText())
        kwargs = {self.widget_name: value}
        function_name = "set" + upper_first_letter(self.widget_name)

        logger.info("set %s parameter to %s" % (function_name, str(kwargs)))
        function = getattr(self.camera_remote.camera_api, function_name)
        await function(**kwargs)

    def make_widget_group_box(self):
        hbox_layout = QtWidgets.QHBoxLayout()

        self.__widget_label = QtWidgets.QLabel("")
        self.__widget_combo_box = QtWidgets.QComboBox()
        self.__widget_combo_box.activated.connect(self.__submit)

        hbox_layout.addWidget(self.__widget_label)
        hbox_layout.addWidget(self.__widget_combo_box)

        group_box = QtWidgets.QGroupBox(self.__group_caption)
        group_box.setLayout(hbox_layout)
        return group_box


class ActionWidget(CameraRemoteWidget):

    def __init__(self, camera_remote, widget_name, button_caption):
        self.camera_remote = camera_remote
        self.widget_name = widget_name
        self.__button_caption = button_caption
        self.__widget_button = None

    def get_event_callback(self):
        return

    @asyncSlot()
    async def __submit(self):
        function_name = self.widget_name

        logger.info("action %s" % (function_name,))
        function = getattr(self.camera_remote.camera_api, function_name)
        await function()

    def make_widget_group_box(self):
        hbox_layout = QtWidgets.QHBoxLayout()
        button = QtWidgets.QPushButton(self.__button_caption)
        button.clicked.connect(self.__submit)
        hbox_layout.addWidget(button)
        group_box = QtWidgets.QGroupBox()

        group_box.setLayout(hbox_layout)
        return group_box


class StartLiveviewWidget(ActionWidget):

    def submit_callback(self, f):
        result = f.result()
        url = result[0]
        self.camera_remote.liveview_task = asyncio.create_task(
            self.camera_remote.download_liveview(url)
        )


class TakePictureWidget(ActionWidget):

    def submit_callback(self, f):
        result = f.result()
        url = result[0][0]
        self.camera_remote.download_task = asyncio.create_task(
            self.camera_remote.download_picture(url)
        )


class WhiteBalanceWidget(CameraRemoteWidget):

    def __init__(self, camera_remote):
        self.camera_remote = camera_remote
        self.widget_name = "whiteBalance"
        self.__white_balance_mode_label = None
        self.__white_balance_mode_combo_box = None
        self.__color_temperature_label = None
        self.__color_temperature_combo_box = None
        self.__white_balance_modes = {}

    def __on_white_balance_mode_changed(self):
        white_balance_mode = self.__white_balance_mode_combo_box.currentText()
        self.__color_temperature_combo_box.clear()
        self.__color_temperature_label.setText("-1")
        if white_balance_mode in self.__white_balance_modes:
            temperature_colors = self.__white_balance_modes[white_balance_mode]
            for temperature_color in temperature_colors:
                self.__color_temperature_combo_box.addItem(str(temperature_color))

    def __get_available_white_balance_callback(self, f):
        result = f.result()
        if result is not None:
            white_balances = result[1]
            if white_balances is not None:
                self.__white_balance_mode_combo_box.clear()
                for white_balance in white_balances:
                    white_balance_mode = white_balance["whiteBalanceMode"]
                    self.__white_balance_mode_combo_box.addItem(white_balance_mode)
                    color_temperature_range = white_balance["colorTemperatureRange"]
                    if color_temperature_range:
                        color_temperatures = range(
                            color_temperature_range[1],
                            color_temperature_range[0] + 1,
                            color_temperature_range[2],
                        )
                        self.__white_balance_modes[white_balance_mode] = color_temperatures

    async def __get_available_white_balance(self):
        task = asyncio.create_task(self.camera_remote.camera_api.getAvailableWhiteBalance())
        task.add_done_callback(self.__get_available_white_balance_callback)

    def event_callback(self, data):
        white_balance_mode = data["currentWhiteBalanceMode"]
        self.__white_balance_mode_label.setText(white_balance_mode)

        color_temperature = data["currentColorTemperature"]
        self.__color_temperature_label.setText(str(color_temperature))

        color_temperature = data["checkAvailability"]
        if color_temperature:
            logger.debug("color temperature: check availability")
            asyncio.create_task(self.__get_available_white_balance())

    def __submit(self):
        white_balance_mode = self.__white_balance_mode_combo_box.currentText()
        color_temperature = self.__color_temperature_combo_box.currentText()
        try:
            int_color_temperature = int(color_temperature)
            color_temperature_enabled = True
        except ValueError:
            int_color_temperature = -1
            color_temperature_enabled = False

        logger.info("set white balance to %s" % (white_balance_mode,))
        asyncio.create_task(
            self.camera_remote.camera_api.setWhiteBalance(
                whiteBalanceMode=white_balance_mode,
                colorTemperatureEnabled=color_temperature_enabled,
                colorTemperature=int_color_temperature
            )
        )

    def make_widget_group_box(self):
        hbox_layout = QtWidgets.QHBoxLayout()

        self.__white_balance_mode_label = QtWidgets.QLabel("")
        self.__white_balance_mode_combo_box = QtWidgets.QComboBox()
        self.__white_balance_mode_combo_box.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.__white_balance_mode_combo_box.activated.connect(self.__on_white_balance_mode_changed)
        white_balance_mode_layout = QtWidgets.QHBoxLayout()
        white_balance_mode_layout.addWidget(self.__white_balance_mode_label)
        white_balance_mode_layout.addWidget(self.__white_balance_mode_combo_box)
        white_balance_mode_group_box = QtWidgets.QGroupBox("White balance mode")
        white_balance_mode_group_box.setLayout(white_balance_mode_layout)

        self.__color_temperature_label = QtWidgets.QLabel("")
        self.__color_temperature_combo_box = QtWidgets.QComboBox()
        color_temperature_layout = QtWidgets.QHBoxLayout()
        color_temperature_layout.addWidget(self.__color_temperature_label)
        color_temperature_layout.addWidget(self.__color_temperature_combo_box)
        color_temperature_group_box = QtWidgets.QGroupBox("Color temperature")
        color_temperature_group_box.setLayout(color_temperature_layout)

        button = QtWidgets.QPushButton("Set white balance")
        button.clicked.connect(self.__submit)

        hbox_layout.addWidget(white_balance_mode_group_box)
        hbox_layout.addWidget(color_temperature_group_box)
        hbox_layout.addWidget(button)

        group_box = QtWidgets.QGroupBox("White balance")
        group_box.setLayout(hbox_layout)
        return group_box


class CameraRemote(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Tabs
        self.__TABS = ["color", "exposure", "flash", "focus", "liveview", "movie", "shoot", "sound"]

        # --- Controls
        self.__WIDGETS = [
            {
                "tab": "color",
                "position": (0, 0),
                "widget": WhiteBalanceWidget(self)
            },
            {
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
                "tab": "exposure",
                "position": (0, 2),
                "widget": CurrentCandidateWidget(self, "fNumber", "F Number")
            },
            {
                "tab": "exposure",
                "position": (1, 0),
                "widget": CurrentCandidateWidget(self, "shutterSpeed", "Shutter Speed")
            },
            {
                "tab": "exposure",
                "position": (1, 1),
                "widget": CurrentCandidateWidget(self, "isoSpeedRate", "Iso speed rate")
            },
            {
                "tab": "flash",
                "position": (0, 0),
                "widget": CurrentCandidateWidget(self, "flashMode", "Flash mode")
            },
            {
                "tab": "focus",
                "position": (0, 0),
                "widget": CurrentCandidateWidget(self, "focusMode", "Focus mode")
            },
            {
                "tab": "liveview",
                "position": (0, 0),
                "widget": StartLiveviewWidget(self, "startLiveview", "Start liveview")
            },
            {
                "tab": "liveview",
                "position": (1, 0),
                "widget": ActionWidget(self, "stopLiveview", "Stop liveview")
            },
            {
                "tab": "movie",
                "position": (0, 0),
                "widget": CurrentCandidateWidget(self, "movieQuality", "Movie Quality")
            },
            {
                "tab": "shoot",
                "position": (0, 0),
                "widget": CurrentCandidateWidget(self, "postviewImageSize", "Postview image size")
            },
            {
                "tab": "shoot",
                "position": (0, 1),
                "widget": CurrentCandidateWidget(self, "steadyMode", "Steady mode")
            },
            {
                "tab": "shoot",
                "position": (0, 2),
                "widget": CurrentCandidateWidget(self, "viewAngle", "View angle")
            },
            {
                "tab": "shoot",
                "position": (1, 0),
                "widget": CurrentCandidateWidget(self, "selfTimer", "Self timer", type_=int)
            },
            {
                "tab": "shoot",
                "position": (1, 1),
                "widget": CurrentCandidateWidget(self, "shootMode", "Shoot mode")
            },
            {
                "tab": "shoot",
                "position": (2, 0),
                "widget": ActionWidget(self, "actHalfPressShutter", "Half press shutter")
            },
            {
                "tab": "shoot",
                "position": (2, 1),
                "widget": ActionWidget(self, "cancelHalfPressShutter", "Cancel half press shutter")
            },
            {
                "tab": "shoot",
                "position": (2, 2),
                "widget": TakePictureWidget(self, "actTakePicture", "Take picture")
            },
            {
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

        self.liveview_task = None
        self.download_task = None

    def __take_picture_callback(self, data):
        urls = data["takePictureUrl"]
        for url in urls:
            self.download_task = asyncio.create_task(self.download_picture(url))

    def __update_status_callback(self, data):
        self.__status_label.setText(data["cameraStatus"])

    async def __device_available_callback(self, device_name, endpoint_url):
        logger.debug("device %s is connected" % (device_name,))

        camera_api = CameraRemoteApi(endpoint_url)
        self.camera_api = camera_api

        events_watcher = await camera_api.initial_checks()
        callbacks = {}
        for widget in self.__WIDGETS:
            callback = widget["widget"].get_event_callback()
            name = widget["widget"].get_name()
            if callback is not None:
                callbacks[name] = callback
        callbacks.update({"cameraStatus": self.__update_status_callback})
        callbacks.update({"takePicture": self.__take_picture_callback})
        events_watcher.register_events(callbacks)
        events_watcher.start_event_watcher()

        await camera_api.startRecMode()

    async def download_liveview(self, url):

        async def load_data(plsize, pdsize):
            with BytesIO() as fd:
                while plsize > 0:
                    chunk = await resp.content.read(plsize)
                    fd.write(chunk)
                    plsize -= len(chunk)
                data = fd.getvalue()
            if pdsize != 0:
                await resp.content.read(pdsize)
            return data

        with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        while True:
                            # read common and payload header
                            headers = await resp.content.read(8 + 128)
                            if headers[0] != 0xff:
                                logger.debug("desynchronized from liveview stream")
                                break
                            # debug_trace()
                            payload_size = 0
                            for byte in headers[12:15]:
                                payload_size *= 256
                                payload_size += byte
                            padding_size = headers[15]
                            if headers[1] == 1:
                                data = await load_data(payload_size, padding_size)
                                pixmap = QtGui.QPixmap()
                                pixmap.loadFromData(QtCore.QByteArray(data))
                                scaled_pixmap = pixmap.scaled(
                                    self.__liveview_view_label.size(),
                                    QtCore.Qt.KeepAspectRatio,
                                    QtCore.Qt.SmoothTransformation
                                )
                                self.__liveview_view_label.setPixmap(scaled_pixmap)
                            else:
                                await load_data(payload_size, padding_size)
            except Exception:
                pass
            self.liveview_task = None

    @asyncSlot()
    async def discover(self):
        await self.__camera_remote_control.discover()

    async def download_picture(self, url):
        with (await self.__download_lock):
            with aiohttp.ClientSession() as session:
                try:
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
                except Exception:
                    pass
            self.download_task = None

    def __init_menu_bar(self):
        menubar = self.menuBar()

        discover_action = QtWidgets.QAction("Discover", self)
        discover_action.triggered.connect(self.discover)

        quit_action = QtWidgets.QAction("Quit", self)
        quit_action.triggered.connect(self.close)

        file_ = menubar.addMenu("File")
        file_.addAction(discover_action)
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

        # --- Liveview view tab
        self.__liveview_view_label = QtWidgets.QLabel()
        self.__liveview_view_label.setAlignment(QtCore.Qt.AlignTop)
        self.__liveview_view_label.setMargin(0)
        liveview_view_layout = QtWidgets.QHBoxLayout()
        liveview_view_layout.addWidget(self.__liveview_view_label)
        liveview_view_layout.setContentsMargins(0, 0, 0, 0)
        liveview_view_widget = QtWidgets.QWidget()
        liveview_view_widget.setLayout(liveview_view_layout)
        tabs.addTab(liveview_view_widget, "liveview view")

        # --- Picture view tab
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

    @asyncSlot()
    async def __button1_callback(self):
        await self.camera_api.getAvailableApiList()

    @asyncSlot()
    async def __button2_callback(self):
        await self.camera_api.getVersions()

    def __pre_close_callback(self):
        self.__closing_actions = True
        self.close()

    @asyncClose
    async def closeEvent(self, event):
        if self.__closing_actions:
            if self.download_task is not None:
                self.download_task.cancel()
            if self.liveview_task is not None:
                self.liveview_task.cancel()
            await self.camera_api.close()
            logger.info("finished")
        else:
            if self.camera_api is not None:
                await self.camera_api.stopRecMode()
                loop = asyncio.get_event_loop()
                loop.call_soon(self.__pre_close_callback)
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

with loop:
    sys.exit(loop.run_forever())

file_handler.close()
