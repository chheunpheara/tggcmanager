from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QGridLayout
)
from TelegramManager import TelegramController
from Worker import Worker
from PyQt6 import QtCore

class DataUpdate(QWidget):
    data_slot = QtCore.pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.telegram = TelegramController()
        self.setWindowTitle('Group and Channel Update')
        self.setMinimumSize(500, 200)
        self.thread_pool = QtCore.QThreadPool()
        self.main_layout = QHBoxLayout()
        self.grid_layout = QGridLayout()

        self.button = QPushButton('Update')
        self.button.setStyleSheet('background: darkblue; height: 40px; border-radius: 10px;')
        self.main_layout.addWidget(self.button)
        self.button.clicked.connect(self.update)

        self.result = QLabel('Tap the button to fetch the updates from Telegram')

        self.grid_layout.addLayout(self.main_layout, 0, 0)
        self.grid_layout.addWidget(self.result, 1, 0)


        self.setLayout(self.grid_layout)

    @QtCore.pyqtSlot()
    def update(self):
        w = Worker(self.update_thread)
        self.thread_pool.start(w)


    def update_thread(self):
        self.result.setText('Fetching updates...')
        self.button.setText('Updating...')
        self.button.setDisabled(True)
        channel, group = self.telegram.sync_groups_channels()
        self.result.setText(f'Total Channel: {channel} | Total group: {group} synced successfully')
        self.button.setText('Update')
        self.button.setEnabled(True)
        self.data_slot.emit({'synchronized': True})


    def closeEvent(self, event):
        self.result.setText('Tap the button to fetch the updates from Telegram')