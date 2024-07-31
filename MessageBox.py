from PyQt6.QtWidgets import QMessageBox
from Constant import Config

def alert(title: str, message: str, type: str = Config.SUCCESS):
    dlg = QMessageBox()
    dlg.setWindowTitle(title)
    dlg.setText(message)
    dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
    
    match type:
        case Config.SUCCESS: dlg.setIcon(QMessageBox.Icon.NoIcon)
        case Config.ERROR: dlg.setIcon(QMessageBox.Icon.Warning)
        case Config.INFORMATION: dlg.setIcon(QMessageBox.Icon.Information)

    dlg.exec()