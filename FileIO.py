from PyQt6 import QtCore
import json


class FileIO(object):
    def write(self, fobj, data: dict, is_text: bool = False):
        fname = QtCore.QFile(fobj)
        if not fname.open(QtCore.QIODevice.OpenModeFlag.ReadWrite | QtCore.QIODevice.OpenModeFlag.Text):
            return (False, 'Unable to open file')
        output = QtCore.QTextStream(fname)
        if is_text:
            output << data
        else: 
            output << data
        return (True, output)


    def read(self, fobj, is_json: bool = True):
        fname = QtCore.QFile(fobj)
        if not fname.open(QtCore.QIODevice.OpenModeFlag.ReadOnly | QtCore.QIODevice.OpenModeFlag.Text):
            return (False, 'Unable to open file')

        data = fname.readAll()
        fname.close()
        if is_json:
            obj = QtCore.QJsonDocument().fromJson(data)
            return (True, obj.toJson().data().decode())
        return (True, data)
