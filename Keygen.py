import os
import myopenssl
import InfoWindow
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QFileDialog, QLineEdit, QDialog
from PyQt5.QtCore import QThread, pyqtSignal

class CryptoWorker(QThread):
    progress = pyqtSignal(str, str)
    finished = pyqtSignal()
 
    def __init__(self, generator):
        super().__init__()
        self.generator = generator

    def run(self):
        try:
            self.progress.emit(self.generator.make_RSA_key(text="-auth"), "green")
            self.progress.emit(self.generator.make_ECDSA_key(), "green")
            self.progress.emit(self.generator.make_CERTIFICATE(), "green")
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}", "red")
        finally:
            self.finished.emit()

class Keygen(QDialog):
    def __init__(self, armi_instance, selected_processor, selected_organization, parent=None):
        super().__init__(parent)
        
        self.armi_instance = armi_instance
        self.selected_organization = selected_organization.lower()
        self.selected_processor = selected_processor
        self.worker = None

        self.selected_armi_number = ""
        self.selected_armi_number_number = ""
        self.directory = ""
        self.textarmi = "armi"
        self.password = ""
        self.aes_dir = ""
        self.keys_dir = ""
        self.time = ""

        self.setWindowTitle("ARMI")
        self.setGeometry(1050, 250, 350, 300)

        self.central_widget = QWidget(self)
        #self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.lable = QHBoxLayout()

        self.lable1 = QLabel("Генерация ключей", self)
        self.lable.addWidget(self.lable1)

        self.main_layout.addLayout(self.lable)

        self.path_to_root = QHBoxLayout()

        self.label_root = QLabel("Путь к корневому сертификату:", self)
        self.path_to_root.addWidget(self.label_root)

        self.button_folder = QPushButton('Выбрать папку')
        self.button_folder.clicked.connect(self.showDialog)
        self.path_to_root.addWidget(self.button_folder)

        self.main_layout.addLayout(self.path_to_root)

        self.text_path = QHBoxLayout()

        self.Output2 = QtWidgets.QTextEdit(self)
        self.Output2.setReadOnly(True)
        self.text_path.addWidget(self.Output2)

        self.main_layout.addLayout(self.text_path)

        self.armi_number = QHBoxLayout()

        self.label_armi_number = QLabel("Номер производства:", self)
        self.armi_number.addWidget(self.label_armi_number)

        self.spin_ARMI = QtWidgets.QSpinBox()
        self.spin_ARMI.setRange(0, 39)  # Устанавливаем диапазон значений
        self.spin_ARMI.setPrefix("00")   # Добавляем ведущий ноль
        self.spin_ARMI.setValue(0)      # Устанавливаем начальное значение
        self.spin_ARMI.valueChanged.connect(self.refresh_selection3)
        self.selected_armi_number = self.spin_ARMI.text()
        self.armi_number.addWidget(self.spin_ARMI)

        self.main_layout.addLayout(self.armi_number)


        self.armi_number_number = QHBoxLayout()

        self.label_armi_number_number = QLabel("Номер ARMI:", self)
        self.armi_number_number.addWidget(self.label_armi_number_number)


        self.spin_ARMI2 = QtWidgets.QSpinBox()
        self.spin_ARMI2.setRange(0, 39)  # Устанавливаем диапазон значений
        self.spin_ARMI2.setPrefix("")   # Добавляем ведущий ноль
        self.spin_ARMI2.setValue(0)      # Устанавливаем начальное значение
        self.spin_ARMI2.valueChanged.connect(self.refresh_selection4)
        self.selected_armi_number_number = self.spin_ARMI2.text()
        self.armi_number_number.addWidget(self.spin_ARMI2)

        self.main_layout.addLayout(self.armi_number_number)
        

        self.src_time = QHBoxLayout()

        self.label_cert_time = QtWidgets.QLabel("Срок сертификата")
        self.src_time.addWidget(self.label_cert_time)

        # Создаем виджет для ввода числа
        self.number_input = QLineEdit(self)
        self.number_input.setPlaceholderText('Введите число дней')
        self.src_time.addWidget(self.number_input)
        self.main_layout.addLayout(self.src_time)

        self.lable_input_password = QHBoxLayout()

        self.text_lable_input_password = QtWidgets.QLabel("Введите пароль")
        self.lable_input_password.addWidget(self.text_lable_input_password)
        self.main_layout.addLayout(self.lable_input_password)

        self.layout_input_password1 = QHBoxLayout()

        self.text_password1 = QtWidgets.QLabel("Пароль: ")
        self.layout_input_password1.addWidget(self.text_password1)

        self.input_password1 = QLineEdit(self)
        self.input_password1.setPlaceholderText('Введите пароль')
        self.layout_input_password1.addWidget(self.input_password1)

        self.main_layout.addLayout(self.layout_input_password1)


        self.layout_input_password2 = QHBoxLayout()

        self.text_password2 = QtWidgets.QLabel("Подтвердите пароль: ")
        self.layout_input_password2.addWidget(self.text_password2)

        self.input_password2 = QLineEdit(self)
        self.input_password2.setPlaceholderText('Введите пароль повторно')
        self.layout_input_password2.addWidget(self.input_password2)

        self.main_layout.addLayout(self.layout_input_password2)



        self.OK = QHBoxLayout()

        self.button_OK = QtWidgets.QPushButton("OK")
        self.button_OK.clicked.connect(lambda: self.check())
        self.OK.addWidget(self.button_OK)

        self.main_layout.addLayout(self.OK)
        self.setLayout(self.main_layout)

#/////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////

    def open_window(self, text):
        self.infowindow = InfoWindow.InfoWindow(text, self)
        self.infowindow.exec_()
    
    def output(self, text, color='black'):
        html_text = f'<font color="{color}">{text}</font>'
        self.Output2.append(html_text)

    def showDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку с корневым сертификатом", options=options)
        self.directory = directory

        if directory:
            self.armi_instance.defprint(f"Your chois ROOT PATH: {directory}")
            self.output(f"Your chois ROOT PATH: {directory}")

    def refresh_selection3(self, text):
        self.selected_armi_number = str(text).zfill(3)

    def refresh_selection4(self, text):
        self.selected_armi_number_number = text

    def check(self):
        time = str(self.number_input.text())
        password1 = str(self.input_password1.text())
        password2 = str(self.input_password2.text())

        self.armi_instance.defprint("|||============|||")

        if self.directory:
            boolean = self.check_path()
            if boolean != True:
                self.directory = ""
            else:
                self.check_files_with_prefix()

        if self.directory == "":
            self.armi_instance.defprint(f"!!! Info: Not path", "red")

        if time == "":
            self.armi_instance.defprint(f"!!! Info: Not time", "red")
        if time == "0":
            time = ""
            self.armi_instance.defprint(f"!!! Info: Time can not be 0", "red")
        if not time.isdigit():
            time = ""
            self.armi_instance.defprint(f"!!! Info: Time can not str ", "red")
        
        if password1 == password2:
            self.password = password1
        if password1 != password2:
            self.password = ""
            self.armi_instance.defprint(f"!!! Info: Passwords don't match", "red")
        if len(password1) <= 7:
            self.password = ""
            self.armi_instance.defprint(f"!!! Info: Password1 is less than 8 characters long", "red")
        if len(password2) <= 7:
            self.password = ""
            self.armi_instance.defprint(f"!!! Info: Password2 is less than 8 characters long", "red")

        if self.directory and time and self.password and self.selected_armi_number_number:
            self.armi_instance.defprint(
                f"Correct Info: {self.directory} {self.textarmi}-"
                f"{self.selected_processor}-{self.selected_organization}-"
                f"{self.selected_armi_number}-{self.selected_armi_number_number}"
                f"  time: {time}  password: {self.password}", "green")

            self.armi_instance.defprint("\n START \n", "yellow")
            self.time = time

            generator = myopenssl.OpenSSLKeyCertGenerator(
                self.keys_dir, self.textarmi, self.selected_processor, 
                self.selected_organization, self.selected_armi_number, 
                self.selected_armi_number_number, self.time, self.password
            )

            self.worker = CryptoWorker(generator)
            self.worker.progress.connect(self.armi_instance.defprint)
            self.worker.finished.connect(self.on_crypto_finished)
            self.button_OK.setEnabled(False)
            self.worker.start()

    def on_crypto_finished(self):
        self.button_OK.setEnabled(True)
        self.open_window(self.directory)
        self.close()

    def check_path(self):
        aes_dir = os.path.join(self.directory, 'aes')
        keys_dir = os.path.join(self.directory, 'keys')

        if not os.path.isdir(aes_dir):
            self.armi_instance.defprint(f"Directory '{aes_dir}' does not exist.", "red")
            return False

        if not os.path.isdir(keys_dir):
            self.armi_instance.defprint(f"Directory '{keys_dir}' does not exist.", "red")
            return False

        aes_master_path = os.path.join(aes_dir, 'aes_master.aes')
        if not os.path.isfile(aes_master_path):
            self.armi_instance.defprint(f"File '{aes_master_path}' does not exist.", "red")
            return False

        keys_files = [
            f"{self.selected_organization.upper()}_armi-root.crt",
            f"{self.selected_organization.upper()}_armi-root.csr",
            f"{self.selected_organization.upper()}_armi-root.ext",
            f"{self.selected_organization.upper()}_armi-root.key",
            f"{self.selected_organization.upper()}_armi-root.key-pwd",
            f"{self.selected_organization.upper()}_armi-root.pub",
        ]

        for file in keys_files:
            file_path = os.path.join(keys_dir, file)
            if not os.path.isfile(file_path):
                self.armi_instance.defprint(f"File '{file_path}' does not exist.", "red")
                return False

        self.armi_instance.defprint("ROOT PATH: All required directories and files are present.", "green")
        self.aes_dir = aes_dir
        self.keys_dir = keys_dir
        return True

    def check_files_with_prefix(self):
        keys_dir = os.path.join(self.directory, 'keys')

        files_to_check = [
            f"{self.selected_organization.upper()}_armi-{self.selected_armi_number}.crt",
            f"{self.selected_organization.upper()}_armi-{self.selected_armi_number}.csr",
            f"{self.selected_organization.upper()}_armi-{self.selected_armi_number}.ext",
            f"{self.selected_organization.upper()}_armi-{self.selected_armi_number}.key",
            f"{self.selected_organization.upper()}_armi-{self.selected_armi_number}.key-pwd",
            f"{self.selected_organization.upper()}_armi-{self.selected_armi_number}.pub",
            f"armi-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}-auth.key",
            f"armi-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}-auth.pub",
            f"armi-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}.csr",
            f"armi-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}.cst",
            f"armi-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}.ext",
            f"armi-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}.key",
            f"armi-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}.key-pwd",
            f"armi-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}.pub",
        ]   

        for file in files_to_check:
            file_path = os.path.join(keys_dir, file)
            if os.path.isfile(file_path):
                self.armi_instance.defprint(f"File '{file_path}' exists.", "red")
                return False

        self.armi_instance.defprint("There are no files", "green")
        return True