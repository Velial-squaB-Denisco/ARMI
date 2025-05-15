import sys
import Keygen
import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget

class MyWindow(QMainWindow):
 
    def __init__(self):
        super().__init__()

        self.selected_organization = ""
        self.selected_processor = ""
        self.all_text = "armi-"

        self.setWindowTitle("Генерация ключей")
        self.setGeometry(300, 250, 350, 300)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.label = QtWidgets.QLabel("ARMI key", self)
        main_layout.addWidget(self.label)

        button_layoutH = QHBoxLayout()
        button_layoutV = QVBoxLayout()

        self.label_processor = QtWidgets.QLabel("Процессор:", self)
        button_layoutH.addWidget(self.label_processor)

        self.combo_processor = QtWidgets.QComboBox()
        self.combo_processor.addItems(["mh", "lpc"])
        self.combo_processor.setFixedWidth(150)
        button_layoutH.addWidget(self.combo_processor)
        self.combo_processor.currentTextChanged.connect(self.refresh_selection1)

        self.label_organization = QtWidgets.QLabel("Вендор:", self)
        button_layoutH.addWidget(self.label_organization)

        self.combo_organization = QtWidgets.QComboBox()
        self.combo_organization.addItems(["PK", "RR"])
        self.combo_organization.setFixedWidth(150)
        button_layoutH.addWidget(self.combo_organization)
        self.combo_organization.currentTextChanged.connect(self.refresh_selection2)

        self.button_armi_keys = QtWidgets.QPushButton("Создать ключи ARMI")
        self.button_armi_keys.clicked.connect(self.open_window)
        button_layoutH.addWidget(self.button_armi_keys)

        main_layout.addLayout(button_layoutH)

        self.Output = QtWidgets.QTextEdit(self)
        self.Output.setReadOnly(True)
        main_layout.addWidget(self.Output)

        self.selected_processor = self.combo_processor.currentText()
        self.selected_organization = self.combo_organization.currentText()
        self.all_text += self.selected_processor + "-" + self.selected_organization

    def defprint(self, text, color='black'):
        html_text = f'<font color="{color}">{text}</font>'
        self.Output.append(html_text)

    def refresh_selection1(self, text):
        self.selected_processor = text

    def refresh_selection2(self, text):
        self.selected_organization = text

    def open_window(self):
        self.defprint(self.all_text)
        self.new_window = Keygen.Keygen(self, self.selected_processor, self.selected_organization)
        self.new_window.exec_()

    def closeEvent(self, event):
        self.running = False
        if self.thread is not None and self.thread.is_alive():
            self.stop()
            self.thread.join()
            self.thread = None

        if self.process is not None:
            self.process.terminate()
            self.process.wait()
            self.process = None

def app():
    application = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(application.exec_())

if __name__ == "__main__":
    app()