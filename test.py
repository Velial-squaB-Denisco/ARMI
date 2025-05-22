import sys
import os
import re
import myopenssl
import threading
import subprocess
import InfoWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QFileDialog, QLineEdit, QSpinBox, QComboBox, QDialog, QTextEdit
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


class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.selected_organization = ""
        self.selected_processor = ""
        self.all_text = "armi-"

        self.worker = None

        self.selected_armi_number = ""
        self.selected_armi_number_number = ""
        self.directory = ""
        self.textarmi = "armi"
        self.password = ""
        self.key_path = ""
        self.crt_path = ""
        self.time = ""

        self.version = False

        self.setWindowTitle("Генерация ключей")
        self.setGeometry(300, 250, 1350, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Левая панель..........................................................................
        left_layout = QVBoxLayout()
        # left_layout.addStretch()
        #.......................................................................................

        self.Output = QtWidgets.QTextEdit(self)
        self.Output.setReadOnly(True)
        left_layout.addWidget(self.Output)

        main_layout.addLayout(left_layout)



        # Правая панель.........................................................................
        right_layout = QVBoxLayout()
        #.......................................................................................
        processor_layout = QHBoxLayout()

        self.label_processor = QtWidgets.QLabel("Процессор:", self)
        processor_layout.addWidget(self.label_processor)


        self.combo_processor = QtWidgets.QComboBox()
        self.combo_processor.addItems(["mh", "lpc"])
        self.combo_processor.setFixedWidth(200)
        processor_layout.addWidget(self.combo_processor)
        self.combo_processor.currentTextChanged.connect(self.refresh_selection1)


        self.label_organization = QtWidgets.QLabel("Вендор:", self)
        processor_layout.addWidget(self.label_organization)


        self.combo_organization = QtWidgets.QComboBox()
        self.combo_organization.addItems(["PK", "RR"])
        self.combo_organization.setFixedWidth(200)
        processor_layout.addWidget(self.combo_organization)
        self.combo_processor.currentTextChanged.connect(self.refresh_selection2)


        keygen_layout = QVBoxLayout()

        self.path_to_root = QHBoxLayout()

        self.label_root = QLabel("Путь в который вы хотите записать файлы:", self)
        self.path_to_root.addWidget(self.label_root)

        self.button_folder = QPushButton('Выбрать папку')
        self.button_folder.clicked.connect(self.showDialog)
        self.path_to_root.addWidget(self.button_folder)

        keygen_layout.addLayout(self.path_to_root)


        self.text_path = QHBoxLayout()

        self.Output2 = QtWidgets.QLineEdit(self)
        self.Output2.setReadOnly(True)
        self.text_path.addWidget(self.Output2)

        keygen_layout.addLayout(self.text_path)


        self.label_key_layout = QHBoxLayout()

        self.label_key = QLabel("Путь к приватному корневому ключу (armi-root.key):", self)
        self.label_key_layout.addWidget(self.label_key)

        self.button_key = QPushButton('Выбрать файл')
        self.button_key.clicked.connect(self.select_key_file)
        self.label_key_layout.addWidget(self.button_key)

        keygen_layout.addLayout(self.label_key_layout)


        self.text_path3 = QHBoxLayout()

        self.Output4 = QtWidgets.QLineEdit(self)
        self.Output4.setReadOnly(True)
        self.text_path3.addWidget(self.Output4)

        keygen_layout.addLayout(self.text_path3)


        self.label_crt_layout = QHBoxLayout()

        self.label_crt = QLabel("Путь к корневому сертификату (armi-root.crt):", self)
        self.label_crt_layout.addWidget(self.label_crt)


        self.button_crt = QPushButton('Выбрать файл')
        self.button_crt.clicked.connect(self.select_crt_file)
        self.label_crt_layout.addWidget(self.button_crt)

        keygen_layout.addLayout(self.label_crt_layout)


        self.text_path2 = QHBoxLayout()

        self.Output3 = QtWidgets.QLineEdit(self)
        self.Output3.setReadOnly(True)
        self.text_path2.addWidget(self.Output3)

        keygen_layout.addLayout(self.text_path2)


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

        keygen_layout.addLayout(self.armi_number)


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

        keygen_layout.addLayout(self.armi_number_number)


        self.src_time = QHBoxLayout()

        self.label_cert_time = QtWidgets.QLabel("Срок сертификата (дней)")
        self.src_time.addWidget(self.label_cert_time)

        # Создаем виджет для ввода числа
        self.number_input = QLineEdit(self)
        self.number_input.setSizePolicy(1, 0)
        self.number_input.setPlaceholderText('Введите число дней')
        # self.number_input.setFixedWidth(265)
        self.number_input.setText("30000")
        self.src_time.addWidget(self.number_input)
        keygen_layout.addLayout(self.src_time)


        self.lable_input_password = QHBoxLayout()

        self.text_lable_input_password = QtWidgets.QLabel("Введите пароль для генерации приватных ключей ARMI")
        self.lable_input_password.addWidget(self.text_lable_input_password)
        keygen_layout.addLayout(self.lable_input_password)

        self.layout_input_password1 = QHBoxLayout()

        self.text_password1 = QtWidgets.QLabel("Пароль: ")
        self.layout_input_password1.addWidget(self.text_password1)

        self.input_password1 = QLineEdit(self)
        self.input_password1.setSizePolicy(1, 0)
        self.input_password1.setPlaceholderText('Введите пароль')
        self.layout_input_password1.addWidget(self.input_password1)

        keygen_layout.addLayout(self.layout_input_password1)


        self.layout_input_password2 = QHBoxLayout()

        self.text_password2 = QtWidgets.QLabel("Подтвердите пароль: ")
        self.layout_input_password2.addWidget(self.text_password2)

        self.input_password2 = QLineEdit(self)
        self.input_password2.setSizePolicy(1, 0)
        self.input_password2.setPlaceholderText('Введите пароль повторно')
        self.layout_input_password2.addWidget(self.input_password2)

        keygen_layout.addLayout(self.layout_input_password2)


        self.OK = QHBoxLayout()

        self.button_OK = QtWidgets.QPushButton("Создать ключи ARMI")
        self.button_OK.clicked.connect(lambda: self.check())
        self.OK.addWidget(self.button_OK)

        keygen_layout.addLayout(self.OK)
        self.setLayout(keygen_layout)





        right_layout.addLayout(processor_layout)
        right_layout.addLayout(keygen_layout)

        main_layout.addLayout(right_layout)

        right_layout.addStretch()




        #.......................................................................................
        #.......................................................................................
        #.......................................................................................
        #Функции
        #.......................................................................................
        #.......................................................................................
        #.......................................................................................

    def open_window(self, text):
        self.infowindow = InfoWindow.InfoWindow(text, self)
        self.infowindow.exec_()

    def defprint(self, text, color='black'):
        html_text = f'<font color="{color}">{text}</font>'
        self.Output.append(html_text)

    def refresh_selection1(self, text):
        self.selected_processor = text

    def refresh_selection2(self, text):
        self.selected_organization = str(text).lower()

    def showDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения файлов", options=options)
        self.directory = directory

        if directory:
            self.defprint(f"Ваш выбранный путь: {directory}")
            self.Output2.setText(directory)

    def select_crt_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите .crt файл",
            "",
            "Certificate Files (*.crt)",
            options=options
        )
        if file_name:
            self.crt_path = file_name
            self.Output3.setText(file_name)

    def select_key_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите .key файл",
            "",
            "Key Files (*.key)",
            options=options
        )
        if file_name:
            self.key_path = file_name
            self.Output4.setText(file_name)

    def refresh_selection3(self, text):
        self.selected_armi_number = str(text).zfill(3)

    def refresh_selection4(self, text):
        self.selected_armi_number_number = text









    def openssl_version(self):
        def parse_openssl_version(version_str):
            parts = re.match(r"OpenSSL (\d+\.\d+\.\d+\w*)", version_str)
            if not parts:
                return None, None, None, version_str
            
            full_version = parts.group(1)
            version_numbers = full_version.split(".")
            
            major = int(version_numbers[0])
            minor = int(version_numbers[1]) if len(version_numbers) > 1 else 0
            patch_level = version_numbers[2] if len(version_numbers) > 2 else "0"
            
            patch = re.match(r"\d+", patch_level).group() if re.match(r"\d+", patch_level) else "0"
            patch = int(patch)
            
            return major, minor, patch, full_version

        try:
            result = subprocess.run(
                ["openssl", "version"], 
                capture_output=True, 
                text=True,
                check=True
            )
            openssl_output = result.stdout.strip()
            self.defprint(f"Обнаружена версия OpenSSL: {openssl_output}")
            
            major, minor, patch, full_version = parse_openssl_version(openssl_output)
            
            if major is None:
                self.defprint("Ошибка: Не удалось распознать версию OpenSSL", "red")
                return False

            is_supported = (
                (major == 1 and minor == 1 and patch >= 1)  
                or (major == 1 and minor > 1)               
                or (major == 2 and minor >= 0)              
            )

            if not is_supported:
                self.defprint(f"Требуется версия OpenSSL >= 1.1.1w и < 3.x.x (ваша версия: {full_version})")
                return False

            if full_version != "1.1.1w":
                self.defprint(f"Тестирование проводилось на версии 1.1.1w (ваша версия: {full_version})")

            return True

        except subprocess.CalledProcessError:
            self.defprint("Ошибка при выполнении команды openssl", "red")
            return False
        except FileNotFoundError:
            self.defprint("OpenSSL не установлен в системе!", "red")
            return False










    def check(self):

        self.selected_processor = self.combo_processor.currentText()
        self.selected_organization = self.combo_organization.currentText().lower()
        self.all_text += self.selected_processor + "-" + self.selected_organization
        
        time = str(self.number_input.text())
        password1 = str(self.input_password1.text())
        password2 = str(self.input_password2.text())

        self.version = self.openssl_version()

        self.defprint("|||============|||")

        if self.directory:
            boolean = False
            if self.directory == "":
                boolean = False
            else:
                boolean = True

            if boolean != True:
                self.directory = ""
            else:
                self.check_files_with_prefix()

        org = ""
        if self.selected_organization == "pk":
            org = f"{self.selected_organization.upper()}_"

        if self.selected_organization == "rr":
            org = ""


        key = ""
        crt = ""

        if self.directory == "":
            self.defprint(f"!!! Info: Not path", "red")

        if self.key_path == "":
            self.defprint(f"!!! Info: Not key", "red")
        else:
            key = f"{org}armi-root.key"

        if self.key_path.split('/')[-1] != (key):
            self.key_path = ""
            self.defprint(f"!!! Info: This is not {self.selected_organization} root key", "red")

        if self.crt_path == "":
            self.defprint(f"!!! Info: Not crt", "red")
        else:
            crt = f"{org}armi-root.crt"

        if self.crt_path.split('/')[-1] != crt:
            self.key_path = ""
            self.defprint(f"!!! Info: This is not {self.selected_organization} root crt", "red")

        if time == "":
            self.defprint(f"!!! Info: Not time", "red")
        if time == "0":
            time = ""
            self.defprint(f"!!! Info: Time can not be 0", "red")
        if not time.isdigit():
            time = ""
            self.defprint(f"!!! Info: Time can not str ", "red")
        
        if password1 == password2:
            self.password = password1
        if password1 != password2:
            self.password = ""
            self.defprint(f"!!! Info: Passwords don't match", "red")
        if len(password1) <= 7:
            self.password = ""
            self.defprint(f"!!! Info: Password1 is less than 8 characters long", "red")
        if len(password2) <= 7:
            self.password = ""
            self.defprint(f"!!! Info: Password2 is less than 8 characters long", "red")

        if self.directory and self.key_path and self.crt_path and time and self.password and self.selected_armi_number_number and self.version:
            self.defprint(
                f"Ваш выбор: {self.directory} {self.textarmi}-"
                f"{self.selected_processor}-{self.selected_organization}-"
                f"{self.selected_armi_number}-{self.selected_armi_number_number}"
                f"  time: {time}  password: {self.password}", "green")

            self.defprint("\n START \n")
            self.time = time

            generator = myopenssl.OpenSSLKeyCertGenerator(
                self.directory, self.textarmi, self.selected_processor, 
                self.selected_organization, self.selected_armi_number, 
                self.selected_armi_number_number, self.time, self.password, self.key_path, self.crt_path
            )

            self.worker = CryptoWorker(generator)
            self.worker.progress.connect(self.defprint)
            self.worker.finished.connect(self.on_crypto_finished)
            self.button_OK.setEnabled(False)
            self.worker.start()

    def on_crypto_finished(self):
        self.button_OK.setEnabled(True)
        t1 = threading.Thread(target=self.open_window(f"{self.directory}\\armi-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}"), daemon=True)
        t1.start()
        t1.join()
        # self.close()


    def check_files_with_prefix(self):
        # keys_dir = os.path.join(self.directory, 'keys')

        if  os.path.isdir(f"{self.directory}\\armi-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}"):
            self.defprint(f"Directory '{self.directory}\\armi-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}' exist.", "red")
            self.directory = ""
            return False

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
            file_path = os.path.join(self.directory, file)
            if os.path.isfile(file_path):
                self.defprint(f"File '{file_path}' exists.", "red")
                return False

        self.defprint("Файлы для перезаписи не найдены", "green")
        return True
    
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
