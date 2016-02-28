#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
import sys

from cameraremoteapi import CameraRemoteApi
from cameraremotecontrol import CameraRemoteControl
from utils import lower_first_letter
from utils import upper_first_letter

# from utils import debug_trace


class Event(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    event_happened = QtCore.pyqtSignal(dict)

    def __init__(self, camera_remote_api):
        self.__camera_remote_api = camera_remote_api

        self.__want_to_stop = False
        self.__is_running = False
        QtCore.QObject.__init__(self)

    def worker(self):
        self.__is_running = True
        self.__want_to_stop = False

        long_polling_flag = False
        while not self.__want_to_stop:
            status, result = self.__camera_remote_api.getEvent(1.0, longPollingFlag=long_polling_flag)
            # print("post event: %s, %s" % (str(status), str(result)))
            if status:
                if result[0] is not None:
                    available_api_list = result[0]["names"]
                    self.__camera_remote_api.set_available_api_list(available_api_list)

                data = {}
                for index in [25, 27, 29, 32]:
                    item = result[index]
                    if type(item) != dict:
                        continue
                    key = item["type"]
                    ckey = upper_first_letter(key)
                    values = {}
                    values["Current"] = item["current" + ckey]
                    try:
                        values["Candidates"] = item[key + "Candidates"]
                    except KeyError:
                        try:
                            min_ = item["min" + ckey]
                            max_ = item["max" + ckey]
                            step = item["stepIndexOf" + ckey]
                            value = min_
                            candidates = []
                            while value <= max_:
                                candidates.append(str(value))
                                value += step
                            values["Candidates"] = candidates
                        except KeyError:
                            continue
                    data[ckey] = values
                if len(data) != 0:
                    self.event_happened.emit(data)
            long_polling_flag = True

        self.__is_running = False
        self.finished.emit()

    def stop(self):
        self.__want_to_stop = True

    def is_running(self):
        return self.__is_running


class CameraRemote(QtGui.QMainWindow):

    # --- Exposure tab
    __EXPOSURE = {
        "ExposureCompensation": {
            "position": (0, 0),
            "type": int,
        },
        "FNumber": {
            "position": (0, 1),
        },
        "ShutterSpeed": {
            "position": (1, 0),
        },
        "IsoSpeedRate": {
            "position": (1, 1),
        },
    }

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.__init_ui()
        self.__camera_remote_api = None
        self.__camera_remote_control = CameraRemoteControl("ILCE", self.__device_available_callback)

        self.__event = None
        self.__thread = None

        self.__want_to_close = False

    def __init_menu_bar(self):
        menubar = self.menuBar()

        quit_action = QtGui.QAction("Quit", self)
        quit_action.triggered.connect(self.close)

        file = menubar.addMenu("File")
        file.addAction(quit_action)

    def log(self, text):
        # NOTE : gui available ?
        self.__text.insertPlainText(text + '\n')

    def __event_received(self, event_params):
        for event_key, event_value in event_params.items():
            for exp in CameraRemote.__EXPOSURE:
                if event_key == exp:
                    label = CameraRemote.__EXPOSURE[event_key]["Label"]
                    combo_box = CameraRemote.__EXPOSURE[event_key]["ComboBox"]
                    current_value = event_value["Current"]
                    label.setText(str(current_value))
                    combo_box.clear()
                    for choice in event_value["Candidates"]:
                        combo_box.addItem(choice)

                    # self.log(str(current_value))

    def __device_available_callback(self, device_name, endpoint_url):
        logging.debug("device %s is connected" % (device_name),)

        camera_remote_api = CameraRemoteApi(endpoint_url)
        self.__camera_remote_api = camera_remote_api
        camera_remote_api.initial_checks()

        self.__event = Event(camera_remote_api)
        self.__thread = QtCore.QThread()
        self.__event.moveToThread(self.__thread)
        self.__event.finished.connect(self.__thread_finished)
        self.__event.event_happened.connect(self.__event_received)
        self.__thread.started.connect(self.__event.worker)

        self.__camera_remote_api.startRecMode()

        self.__thread.start()

    def __submit(self):
        if self.__camera_remote_api is None:
            return

        sender = self.sender()

        function_name = str(sender.objectName())
        param_name = lower_first_letter(function_name)
        value = sender.currentText()
        type_ = CameraRemote.__EXPOSURE[function_name].get("type", str)
        value = type_(value)

        function_name = "set" + function_name
        set_function = getattr(self.__camera_remote_api, function_name)
        kwargs = {param_name: value}
        set_function(**kwargs)

    def __start_action(self):
        if self.__event is not None:
            self.log("start")
            self.__thread.start()

    def __stop_action(self):
        if self.__event is not None:
            self.__event.stop()
            self.log("stop")

    def __init_ui(self):

        self.__text = QtGui.QTextBrowser(self)

        layout_exposure = QtGui.QGridLayout()
        for exp in CameraRemote.__EXPOSURE:
            label = QtGui.QLabel("")

            combo_box = QtGui.QComboBox()
            combo_box.setObjectName(exp)
            combo_box.activated.connect(self.__submit)

            hbox_layout = QtGui.QHBoxLayout()
            hbox_layout.addWidget(label)
            hbox_layout.addWidget(combo_box)

            gb = QtGui.QGroupBox(exp)
            gb.setLayout(hbox_layout)

            layout_exposure.addWidget(gb, *CameraRemote.__EXPOSURE[exp]["position"])
            CameraRemote.__EXPOSURE[exp]["Label"] = label
            CameraRemote.__EXPOSURE[exp]["ComboBox"] = combo_box

        widget_exposure = QtGui.QWidget()
        widget_exposure.setLayout(layout_exposure)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        layout_exposure.addLayout(hbox, 0, 2, 2, 1)
        vbox = QtGui.QVBoxLayout()
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
        self.label = QtGui.QLabel()
        pixmap = QtGui.QPixmap(640, 480)
        pixmap.fill(Qt.red)
        self.label.setPixmap(pixmap)

        # ---Test tab
        button_start = QtGui.QPushButton("start")
        button_stop = QtGui.QPushButton("stop")
        layout_test = QtGui.QHBoxLayout()
        layout_test.addWidget(button_start)
        layout_test.addWidget(button_stop)

        widget_test = QtGui.QWidget()
        widget_test.setLayout(layout_test)

        button_start.clicked.connect(self.__start_action)
        button_stop.clicked.connect(self.__stop_action)

        # ---

        tabs = QtGui.QTabWidget()
        tabs.addTab(widget_exposure, "Exposure")
        tabs.addTab(self.label, "Shoot")
        tabs.addTab(widget_test, "Test")

        layout = QtGui.QGridLayout()
        layout.addWidget(tabs, 0, 0)
        layout.addWidget(self.__text, 1, 0)

        # create a window and add the layout
        window = QtGui.QWidget()
        window.setLayout(layout)

        self.__init_menu_bar()

        self.setCentralWidget(window)
        self.setWindowTitle("Camera Remote")

        self.statusBar().showMessage("Ready")

        # x and y coordinates on the screen, width, height
        self.setGeometry(100, 100, 1030, 800)

    def __thread_finished(self):
        self.__thread.quit()
        if self.__want_to_close:
            self.__want_to_close = False
            self.close()

    def closeEvent(self, event):
        if self.__event is not None:
            if self.__event.is_running():
                self.__event.stop()
                self.__want_to_close = True
                event.ignore()
                return
        if self.__camera_remote_api is not None:
            self.__camera_remote_api.stopRecMode()
        logging.info("finished")
        event.accept()


def main():
    log_filename = os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".log"
    logging.basicConfig(
        filename=log_filename ,
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG,
        filemode='w'
    )
    logging.info("started")

    app = QtGui.QApplication(sys.argv)

    camera_remote = CameraRemote()
    camera_remote.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
