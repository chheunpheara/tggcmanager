from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QGridLayout,
    QWidget,
    QRadioButton,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QCheckBox,
    QPushButton,
    QFileDialog
)
from PyQt6 import QtCore, QtGui
from TelegramManager import TelegramController
from ChannelGroupWidget import DataUpdate
from BotWidget import BotManager
from Constant import Config
from MessageBox import (
    alert
)
from Worker import Worker
import os

base_dir = os.path.dirname(__file__)

class MainApplication(QMainWindow):
    main_data_slot = QtCore.pyqtSignal(dict)
    main_bot_slot = QtCore.pyqtSignal(dict)
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.telegram = TelegramController()
        self.bot_widget = BotManager()
        self.setStyleSheet(
            '''
            #Body {background: #eee;}
            #MessageBox {border: 1px solid #000; background: #fff; color: #000}
            QListWidget {color: #000; border: 0}
            QLabel {color: #000; font-weight: bold}
            QRadioButton {color: #000;}
            QPushButton {color: #fff; height: 40px; border-radius: 5px; background: darkblue}
            QCheckBox {color: #000}
            '''
        )
        self.setWindowTitle('Telegram Group|Channel Manager')
        self.radio_state = {}
        self.pictures = []
        self.videos = []
        self.docs = []
        self.setObjectName('Body')
        self.setMinimumSize(1000, 400)
        self.menu = self.menuBar()
        self.menu.setNativeMenuBar(False)

        self.thread_pool = QtCore.QThreadPool()
        self.target = {}
        self.channels = self.telegram.get_groups_channels([Config.CHAT_TYPE_CHANNEL])
        self.groups = self.telegram.get_groups_channels([Config.CHAT_TYPE_GROUP, Config.CHAT_TYPE_SUPER_GROUP])
        self.main_layout = QGridLayout()
        self.content_layout = QVBoxLayout()
        self.content_hlayout = QHBoxLayout()
        self.group_layout = QVBoxLayout()
        self.channel_layout = QVBoxLayout()

        # Setup menu
        self.setup_menu()

        self.reload_button = QPushButton('Reload')
        self.reload_button.clicked.connect(self.reload_groups_channels)
        # self.main_layout.addWidget(self.reload_button, 0, 1)
        # Setup layout
        self.setup_content_layout()
        self.setup_group_layout()
        self.setup_channel_layout()

        # Connect slot
        self.data_slot = DataUpdate()
        self.data_slot.data_slot.connect(self.get_data_update)
        self.bot_widget.bot_slot.connect(self.get_bot_update)
        self.main_data_slot.connect(self.data_slot.update)
        self.main_bot_slot.connect(self.bot_widget.configure)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)
        self.main_layout.addWidget(self.send_button, 3, 0, 1, 2)

        self.text_length = QLabel(f'Max: {Config.TELEGRAM_MESSAGE_LIMIT}')
        self.text_length.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.text_length, 3, 2)

        self.main_layout.setRowStretch(3, 1)
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)
        # self.showFullScreen()

    def setup_picture_layout(self):
        self.browse = QPushButton('Browse')
        self.browse.setStyleSheet('background: pink;color: #000')

        self.browse_vdo = QPushButton('Browse')
        self.browse_vdo.setStyleSheet('background: pink;color: #000')

        self.browse_doc = QPushButton('Browse')
        self.browse_doc.setStyleSheet('background: pink;color: #000')

        self.picture_layout = QGridLayout()
        self.content_layout.addLayout(self.picture_layout)
        self.browse.clicked.connect(self.on_browse)
        self.browse_vdo.clicked.connect(self.on_browse)
        self.browse_doc.clicked.connect(self.on_browse)


    def setup_content_layout(self):
        self.radio_text = QRadioButton('Message')
        self.radio_text.setChecked(True)
        self.radio_picture = QRadioButton('Picture')

        self.radio_video = QRadioButton('Video')
        # self.radio_video.setStyleSheet('color: #aaa')
        # self.radio_video.setDisabled(True)

        self.radio_doc = QRadioButton('Document')
        # self.radio_doc.setStyleSheet('color: #aaa')
        # self.radio_doc.setDisabled(True)

        self.radio_text.toggled.connect(self.switch_option)
        self.radio_picture.toggled.connect(self.switch_option)
        self.radio_doc.toggled.connect(self.switch_option)
        self.radio_video.toggled.connect(self.switch_option)

        self.message_layout = QVBoxLayout()

        self.message_box = QPlainTextEdit()
        self.message_box.textChanged.connect(self.on_text_changed)
        self.message_box.setPlaceholderText('Enter your message here')
        self.message_box.setObjectName('MessageBox')

        self.content_hlayout.addWidget(self.radio_text)
        self.content_hlayout.addWidget(self.radio_picture)
        self.content_hlayout.addWidget(self.radio_video)
        self.content_hlayout.addWidget(self.radio_doc)
        self.content_layout.addLayout(self.content_hlayout)

        self.message_layout.addWidget(self.message_box)
        self.content_layout.addLayout(self.message_layout)
        self.main_layout.addLayout(self.content_layout, 1, 0, 2, 3)


    def switch_option(self):
        state = self.radio_state
        
        if self.radio_text.isChecked():
            if ('option' in state and state['checked'] and state['option'] == 'message'): return
            self.radio_state = {'checked': True, 'option': 'message'}
            self.text_length.setText(f'Max: {Config.TELEGRAM_MESSAGE_LIMIT}')
            self.reset_resource_layout()
            if hasattr(self, 'browse'): self.browse.hide()
            if hasattr(self, 'browse_vdo'): self.browse_vdo.hide()
            if hasattr(self, 'browse_doc'): self.browse_doc.hide()

        if self.radio_picture.isChecked():
            if ('option' in state and state['checked'] and state['option'] == 'picture'): return
            if self.docs or self.videos: self.reset_resource_layout()
            self.radio_state = {'checked': True, 'option': 'picture'}
            if hasattr(self, 'browse_vdo'): self.browse_vdo.hide()
            if hasattr(self, 'browse_doc'): self. browse_doc.hide()
            self.setup_picture_layout()
            self.picture_layout.addWidget(self.browse)
            self.text_length.setText(f'Max: {Config.TELEGRAM_CAPTION_LIMIT}')


        if self.radio_video.isChecked():
            if ('option' in state and state['checked'] and state['option'] == 'video'): return
            if self.pictures: self.reset_resource_layout()

            self.radio_state = {'checked': True, 'option': 'video'}
            if hasattr(self, 'browse'): self.browse.hide()
            if hasattr(self, 'browse_doc'): self.browse_doc.hide()
            self.setup_picture_layout()
            self.picture_layout.addWidget(self.browse_vdo)
            self.text_length.setText(f'Max: {Config.TELEGRAM_CAPTION_LIMIT}')


        if self.radio_doc.isChecked():
            if ('option' in state and state['checked'] and state['option'] == 'doc'): return
            if self.pictures or self.videos: self.reset_resource_layout()
            self.radio_state = {'checked': True, 'option': 'doc'}
            if hasattr(self, 'browse'): self.browse.hide()
            if hasattr(self, 'browse_vdo'): self.browse_vdo.hide()
            self.setup_picture_layout()
            self.picture_layout.addWidget(self.browse_doc)
            self.text_length.setText(f'Max: {Config.TELEGRAM_CAPTION_LIMIT}')


    def reset_resource_layout(self, skip_first_row: bool = True):
        for i in reversed(range(self.picture_layout.count())):
            if skip_first_row and i == 0: continue
            self.picture_layout.takeAt(i).widget().setParent(None)


    def on_browse(self):
        allowed_files = 'Images (*.png *.jpeg *.jpg *.gif);;'
        if self.radio_video.isChecked():
            allowed_files = 'Videos (*.mp4);;'
        if self.radio_doc.isChecked():
            allowed_files = 'Files (*.docx *.xlsx *.txt *.pdf *.ppt);;'
        self.files = QFileDialog.getOpenFileNames(self, 'Open Files', '${HOME}', allowed_files)
        if len(self.files[0]) > 10:
            alert('Error', 'Maximum of 10 photos allowed', Config.ERROR)
            return
        
        if self.radio_picture.isChecked():
            self.pictures = self.files[0]
            row = 0
            col = 0
            for i, f in enumerate(self.files[0]):
                lbl = QLabel()
                pic = QtGui.QPixmap(f)
                lbl.setPixmap(pic.scaled(100, 100, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
                lbl.setScaledContents(True)
                if i % 5 == 0:
                    row += 1
                    col = 0
                else:
                    col += 1
                self.picture_layout.addWidget(lbl, row, col)

        if self.radio_video.isChecked() or self.radio_doc.isChecked():
            self.videos = self.docs = self.files[0]
            row = 0
            col = 0
            for i, f in enumerate(self.files[0]):
                fname = f.split('/')
                lbl = QLabel(fname[len(fname) - 1])
                row += 1
                self.picture_layout.addWidget(lbl, row, col)


    def on_text_changed(self):
        try:
            text = self.message_box.toPlainText()
            max_length = int(Config.TELEGRAM_MESSAGE_LIMIT)
            if self.radio_picture.isChecked():
                max_length = int(Config.TELEGRAM_CAPTION_LIMIT)
            remaining = max_length - len(text)
            if remaining < 0:
                text = text[:max_length]
                self.message_box.setPlainText(text)
                self.message_box.viewport().setCursor(QtCore.Qt.CursorShape.WaitCursor)
                remaining += 1
            # self.message_box.setTextCursor(self.message_box.textCursor())
            self.text_length.setText(f'Max: {str(remaining)}')
        except: pass


    def setup_group_layout(self):
        self.group_label = QLabel('Groups')
        self.group_list = QGridLayout()
        if self.groups:
            self.group_layout.addWidget(self.group_label)
            self.group_data()

        self.group_layout.addLayout(self.group_list)
        self.group_list.setRowStretch(10, 1)
        self.main_layout.addLayout(self.group_layout, 1, 4, 1, 3)


    def group_data(self):
        self.groups = self.telegram.get_groups_channels([Config.CHAT_TYPE_GROUP, Config.CHAT_TYPE_SUPER_GROUP])
            
        for i, g in enumerate(self.groups):
            title = g['title']
            short_title = title[:30] + '...' if len(title) > 30 else title
            tg = QCheckBox(short_title)
            tg.setToolTip(title)
            tg.setObjectName(f"group_{g['id']}")
            tg.checkStateChanged.connect(self.check_box)
            self.group_list.addWidget(tg, i + 1, 0)


    def uncheck_boxes(self):
        qboxes = self.findChildren(QCheckBox)
        for box in qboxes:
            box.setChecked(False)


    def check_box(self, tg):
        qboxes = self.findChildren(QCheckBox)
        for box in qboxes:
            item = box.objectName()
            if item.startswith('group') and box.isChecked():
                _, group = item.split('_')
                self.target[group] = 'group'

            if item.startswith('channel') and box.isChecked():
                _, channel = item.split('_')
                self.target[channel] = 'channel'


    def setup_channel_layout(self):
        self.channel_label = QLabel('Channels')
        self.channel_list = QGridLayout()
        if self.channels:
            self.channel_layout.addWidget(self.channel_label)
            self.update_channel_data()
        self.channel_layout.addLayout(self.channel_list)
        self.channel_list.setRowStretch(10, 1)
        self.main_layout.addLayout(self.channel_layout, 1, 6, 1, 3)


    def update_channel_data(self, clear: bool = False):
        if clear:
            self.channels = self.telegram.get_groups_channels([Config.CHAT_TYPE_CHANNEL])

        for i, c in enumerate(self.channels):
            title = c['title']
            short_title = title[:30] + '...' if len(title) > 30 else title
            tc = QCheckBox(short_title)
            tc.setToolTip(title)
            tc.setObjectName(f"channel_{c['id']}")
            tc.checkStateChanged.connect(self.check_box)
            self.channel_list.addWidget(tc, i + 1, 0)


    def setup_menu(self):
        self.file_menu = self.menu.addMenu('File')
        self.menu_exit = QtGui.QAction(QtGui.QIcon(os.path.join(base_dir, 'icons/exit.png')), 'Exit')
        self.file_menu.addAction(self.menu_exit)
        self.menu_exit.triggered.connect(lambda: QApplication.quit())

        self.setting_menu = self.menu.addMenu('Settings')
        self.setting_bot = QtGui.QAction(QtGui.QIcon(os.path.join(base_dir, 'icons/bot.png')), 'Bots')
        self.setting_bot.triggered.connect(lambda: self.bot_widget.show())

        self.setting_group = QtGui.QAction(QtGui.QIcon(os.path.join(base_dir, 'icons/group.png')), 'Groups & Channel')
        self.setting_menu.addAction(self.setting_bot)
        self.setting_menu.addSeparator()
        self.setting_menu.addAction(self.setting_group)
        self.setting_group.triggered.connect(lambda: self.data_slot.show())


    def send_message(self):
        self.telegram = TelegramController()
        self.send_button.setText('Sending...')
        self.send_button.setDisabled(True)
        if not self.target.keys():
            alert('Information', 'No group has been selected', Config.INFORMATION)
            self.send_button.setText('Send')
            self.send_button.setEnabled(True)
            return
        
        if self.radio_text.isChecked():
            message = self.message_box.toPlainText()
            if not message or (message and not message.strip()):
                alert('Information', 'No message has been set', Config.INFORMATION)
                self.send_button.setText('Send')
                self.send_button.setEnabled(True)
                return
            
        method = self.send_message_thread
        if self.radio_picture.isChecked():
            method = self.send_thread_pictures

        if self.radio_video.isChecked():
            method = self.send_thread_videos

        if self.radio_doc.isChecked():
            method = self.send_thread_docs
        
        w = Worker(method)
        self.thread_pool.start(w)


    def send_message_thread(self):
        groups = self.target.keys()
        self.telegram.broadcast_message(self.message_box.toPlainText(), groups)
        self.send_button.setText('Send')
        self.send_button.setEnabled(True)


    def send_thread_pictures(self):
        groups = self.target.keys()
        res = self.telegram.send_thread_pictures(groups, self.files[0], caption=self.message_box.toPlainText())
        self.send_button.setText('Send')
        self.send_button.setEnabled(True)

    def send_thread_videos(self):
        groups = self.target.keys()
        res = self.telegram.send_thread_videos(groups, self.files[0], caption=self.message_box.toPlainText())
        self.send_button.setText('Send')
        self.send_button.setEnabled(True)


    def send_thread_docs(self):
        groups = self.target.keys()
        res = self.telegram.send_thread_docs(groups, self.files[0], caption=self.message_box.toPlainText())
        self.send_button.setText('Send')
        self.send_button.setEnabled(True)


    @QtCore.pyqtSlot(dict)
    def get_data_update(self, data):
        if 'synchronized' in data and data['synchronized']:
            self.telegram = TelegramController()
            self.channels = self.telegram.get_groups_channels([Config.CHAT_TYPE_CHANNEL])
            self.groups = self.telegram.get_groups_channels([Config.CHAT_TYPE_GROUP, Config.CHAT_TYPE_SUPER_GROUP])
            self.uncheck_boxes()
            if self.groups:
                for i in reversed(range(self.group_list.count())):
                    self.group_label.setHidden(True)
                    self.group_list.itemAt(i).widget().setParent(None)
                
                self.group_list.deleteLater()
            self.setup_group_layout()

            if self.channels:
                for i in reversed(range(self.channel_list.count())):
                    self.channel_label.setHidden(True)
                    self.channel_list.itemAt(i).widget().setParent(None)

                self.channel_list.deleteLater()
            self.channels = self.telegram.get_groups_channels([Config.CHAT_TYPE_CHANNEL])
            self.setup_channel_layout()
    

    @QtCore.pyqtSlot(dict)
    def get_bot_update(self, data):
        if 'bot_configured' in data and data['bot_configured']:
            self.telegram = TelegramController()
            self.data_slot = DataUpdate()
            self.data_slot.data_slot.connect(self.get_data_update)


    def reload_groups_channels(self):
        self.reload_button.setText('Reloading update...')
        self.reload_button.setDisabled(True)
        self.reload_button.setText('Reload')
        self.reload_button.setEnabled(True)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = MainApplication()
    window.show()
    app.exec()