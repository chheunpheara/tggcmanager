from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QPushButton,
    QLabel,
    QVBoxLayout
)
from TelegramManager import TelegramController
from MessageBox import alert
from Constant import Config

class BotManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('Body')
        self.setStyleSheet(
            '''
            #ConfigureButton {background: darkblue; color: #fff; height: 40px; border-radius: 5px;}
            QLineEdit {background: #fff; border: 1px solid #aaa; height: 30px; border-radius: 5px; color: #000; font-size: 14px}
            '''
        )

        self.setWindowTitle('Bot Coniguration')
        self.telegram = TelegramController()
        self.setMinimumSize(400, 200)

        self.main_layout = QVBoxLayout()

        self.bot_name = QLineEdit()
        self.bot_name.setPlaceholderText('Bot Title')

        self.bot_username = QLineEdit()
        self.bot_username.setPlaceholderText('Bot Username')

        self.bot_token = QLineEdit()
        self.bot_token.setPlaceholderText('Bot Token')

        self.configure_button = QPushButton('Configure')
        self.configure_button.setObjectName('ConfigureButton')

        self.current_bot = QLabel()
        self.get_bot()
        self.main_layout.addWidget(self.bot_name)
        self.main_layout.addWidget(self.bot_username)
        self.main_layout.addWidget(self.bot_token)
        self.main_layout.addWidget(self.configure_button)
        self.main_layout.addWidget(self.current_bot)
        
        self.configure_button.clicked.connect(self.configure)
        self.setLayout(self.main_layout)

    def get_bot(self):
        self.updates = self.telegram.show_bots()
        for bot in self.updates:
            self.current_bot.setText(f'Bot in Use: {bot["name"]}, Username: {bot["username"]}')

    def configure(self):
        self.configure_button.setText('Saving...')
        self.configure_button.setDisabled(True)
        
        bot_name = self.bot_name.text()
        bot_token = self.bot_token.text()
        bot_username = self.bot_username.text()

        if (not bot_name or (bot_name and not bot_name.strip())):
            alert('Error', 'Bot name is required', Config.ERROR)
            self.configure_button.setText('Configure')
            self.configure_button.setEnabled(True)
            return
        
        if (not bot_username or (bot_username and not bot_username.strip())):
            alert('Error', 'Bot username is required', Config.ERROR)
            self.configure_button.setText('Configure')
            self.configure_button.setEnabled(True)
            return
        
        if (not bot_token or (bot_token and not bot_token.strip())):
            alert('Error', 'Bot token is required', Config.ERROR)
            self.configure_button.setText('Configure')
            self.configure_button.setEnabled(True)
            return
        
        status = self.telegram.configure_bot(
            bot_name=bot_name,
            bot_username=bot_username,
            bot_token=bot_token
        )

        if not status:
            alert('Error', 'Unable to configure bot. Please try again!', Config.ERROR)
            self.configure_button.setText('Configure')
            self.configure_button.setEnabled(True)
            return
        
        alert('Success', 'Bot has been successfully configured', Config.SUCCESS)
        self.get_bot()
        self.configure_button.setText('Configure')
        self.configure_button.setEnabled(True)
        self.bot_name.setText(str(status))
