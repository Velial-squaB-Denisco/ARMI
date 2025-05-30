from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog


class InfoWindow(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)

        self.text_content = f"Ваши файлы сохранены в: {text}"

        self.setWindowTitle("Info")
        self.setGeometry(1050, 250, 200, 200)

        self.main_layout = QVBoxLayout(self)

        self.text_layout = QHBoxLayout()

        self.Output3 = QLabel(self.text_content, self)
        self.text_layout.addWidget(self.Output3)

        self.main_layout.addLayout(self.text_layout)

        self.button_layout = QHBoxLayout()

        self.button = QPushButton("Ok")

        self.button.clicked.connect(self.close)
        self.button_layout.addWidget(self.button)

        self.main_layout.addLayout(self.button_layout)
