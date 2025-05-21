import os
import subprocess
import re


 
# Константы для ошибок
ERR_WRONG_PREFIX = -1
ERR_UNKNOWN = -2
ERR_AES_KEY = -3

class OpenSSLKeyCertGenerator:
    def __init__(self, keys_dir, textarmi, selected_processor, selected_organization, selected_armi_number, selected_armi_number_number, time ,password, key_path, crt_path):
        self.keys_dir = keys_dir
        self.textarmi = textarmi
        self.selected_processor = selected_processor
        self.selected_organization = selected_organization
        self.selected_armi_number = selected_armi_number
        self.selected_armi_number_number = selected_armi_number_number
        self.time = time
        self.password = password
        self.key_path = key_path
        self.crt_path = crt_path

        self.ECDSA_key = ""

        self.folder_name = str(f"{self.textarmi}-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}")
        self.folder_path = str(f"{self.keys_dir}\{self.folder_name}")
        os.makedirs(self.folder_path, exist_ok=True)

        self.prefix = str(f"{self.folder_path}\{self.textarmi}-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}")

        # Переменные для хранения результата и выводов
        self.result = 0
        self.output = ""
        self.stdout = ""

    def run(self, command, add_stdout=True):
        # Метод выполнения команд через subprocess
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        stdout, _ = process.communicate()
        self.stdout = stdout
        self.result = process.returncode
        if add_stdout:
            self.output += stdout + "\n"

    def make_RSA_key(self, text=""):

        keys_folder_name = "RSA_key"
        keys_folder = str(f"{self.folder_path}\{keys_folder_name}")
        os.makedirs(keys_folder, exist_ok=True)

        self.folder_path = str(f"{self.keys_dir}\{self.folder_name}\{keys_folder_name}")
        self.prefix = str(f"{self.folder_path}\{self.textarmi}-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}")
        
        # Определяем пути для сохранения ключей
        private_key_path = self.prefix + text + ".key"
        public_key_path = self.prefix + text + ".pub"
        private_key_pwd_path = self.prefix + text + ".key-pwd"
        
        
        # Команда для генерации приватного ключа
        # generate_private_key_cmd = [
        #     'openssl', 'genpkey',
        #     '-algorithm', 'RSA',
        #     '-out', private_key_path,
        #     '-pkeyopt', 'rsa_keygen_bits:2048'
        # ]


        # 1. Генерация ключа в формате PKCS#1 (устаревший метод)
        generate_private_key_cmd = [
            'openssl', 'genrsa',             
            '-out', private_key_path,
            '2048'                           
        ]
        # Команда для извлечения публичного ключа из приватного
        generate_public_key_cmd = [
            'openssl', 'rsa',
            '-pubout',
            '-in', private_key_path,
            '-out', public_key_path
        ]

        generate_private_key_pwd_cmd = [
            'openssl', 'rsa',
            '-in', private_key_path,
            '-out', private_key_pwd_path,
            '-aes-128-cbc',
            '-passout', f'pass:{self.password}'
        ]
        # Выполнение команд
        subprocess.run(generate_private_key_cmd, check=True)
        subprocess.run(generate_public_key_cmd, check=True)
        subprocess.run(generate_private_key_pwd_cmd, check=True)

        self.folder_path = str(f"{self.keys_dir}\{self.folder_name}")

        return f"Ключи успешно созданы и сохранены в {private_key_path} и {public_key_path}."
    
    def make_ECDSA_key(self):
        keys_folder_name = "ECDSA_KEYS"
        keys_folder = str(f"{self.folder_path}\{keys_folder_name}")
        os.makedirs(keys_folder, exist_ok=True)

        self.folder_path = str(f"{self.keys_dir}\{self.folder_name}\{keys_folder_name}")
        self.prefix = str(f"{self.folder_path}\{self.textarmi}-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}")

        # Определяем пути для сохранения ключей
        private_key_path = self.prefix + ".key"
        public_key_path = self.prefix + ".pub"
        private_key_pwd_path = self.prefix + ".key-pwd"

        self.ECDSA_key = private_key_path

        # Команда для генерации приватного эллиптического ключа
        generate_private_key_cmd = [
            'openssl', 'ecparam', '-genkey', '-noout', '-name', 'prime256v1', '-out', private_key_path
        ]

        # Команда для извлечения публичного ключа из приватного
        generate_public_key_cmd = [
            'openssl', 'ec', '-in', private_key_path, '-pubout', '-out', public_key_path
        ]

        generate_private_key_pwd_cmd = [
            'openssl', 'ec',
            '-in', private_key_path,
            '-out', private_key_pwd_path,
            '-aes-128-cbc',
            '-passout', f'pass:{self.password}'
        ]

        # Выполнение команд
        subprocess.run(generate_private_key_cmd, check=True)
        subprocess.run(generate_public_key_cmd, check=True)
        subprocess.run(generate_private_key_pwd_cmd, check=True)

        self.folder_path = str(f"{self.keys_dir}\{self.folder_name}")

        return f"Эллиптические ключи успешно созданы и сохранены в {private_key_path} и {public_key_path}"
    
    def make_RSA_2048_key(self):
        
        # Определяем пути для сохранения ключей
        private_key_path = self.prefix + '(RSA_2048).key'
        public_key_path = self.prefix + '(RSA_2048).pub'
        private_key_pwd_path = self.prefix + "(RSA_2048).key-pwd"

        # Команда для генерации приватного RSA-2048 ключа
        generate_private_key_cmd = [
            'openssl', 'genpkey',
            '-algorithm', 'RSA',
            '-out', private_key_path,
            '-pkeyopt', 'rsa_keygen_bits:2048'
        ]

        # Команда для извлечения публичного ключа из приватного
        generate_public_key_cmd = [
            'openssl', 'rsa',
            '-pubout',
            '-in', private_key_path,
            '-out', public_key_path
        ]

        generate_private_key_pwd_cmd = [
            'openssl', 'genpkey',
            '-algorithm', 'RSA',
            '-out', private_key_pwd_path,
            '-aes-128-cbc',
            '-pass', f'pass:{self.password}',  # Установка пароля
            '-pkeyopt', 'rsa_keygen_bits:2048'
        ]

        # Выполнение команд
        subprocess.run(generate_private_key_cmd, check=True)
        subprocess.run(generate_public_key_cmd, check=True)
        subprocess.run(generate_private_key_pwd_cmd, check=True)

        return f"RSA-2048 ключи успешно созданы и сохранены в {private_key_path} и {public_key_path}"

    def make_CERTIFICATE_self(self):

        # Пути для сохранения ключей и сертификата
        private_key_path = 'private_key.key'
        csr_path = 'certificate.csr'
        crt_path = 'certificate.crt'

        # Команда для генерации приватного ключа
        generate_private_key_cmd = [
            'openssl', 'genpkey',
            '-algorithm', 'RSA',
            '-out', private_key_path,
            '-pkeyopt', 'rsa_keygen_bits:2048'
        ]

        # Команда для создания CSR
        generate_csr_cmd = [
            'openssl', 'req', '-new',
            '-key', private_key_path,
            '-out', csr_path,
            '-subj', '/C=RU/ST=Moscow/L=Moscow/O=AQSI/CN=AQSI_xxx'
        ]

        # Команда для создания самоподписанного сертификата
        generate_crt_cmd = [
            'openssl', 'x509', '-req',
            '-days', self.time,
            '-in', csr_path,
            '-signkey', private_key_path,
            '-out', crt_path
        ]

        # Выполнение команд
        subprocess.run(generate_private_key_cmd, check=True)
        subprocess.run(generate_csr_cmd, check=True)
        subprocess.run(generate_crt_cmd, check=True)

        return f"Сертификат успешно создан и сохранен в файл {crt_path}"
    

    def make_CERTIFICATE(self):
        keys_folder_name = "CERTIFICATE"
        keys_folder = str(f"{self.folder_path}\{keys_folder_name}")
        os.makedirs(keys_folder, exist_ok=True)

        self.folder_path = str(f"{self.keys_dir}\{self.folder_name}\{keys_folder_name}")
        self.prefix = str(f"{self.folder_path}\{self.textarmi}-{self.selected_processor}-{self.selected_organization}-{self.selected_armi_number}-{self.selected_armi_number_number}")
        

        ca_key_path = self.key_path  # Путь к приватному ключу CA
        ca_crt_path = self.crt_path  # Путь к корневому сертификату CA
        server_csr_path = self.prefix + '.csr'
        server_crt_path = self.prefix + '.crt'
            
        ext_file_path = self.prefix + '.ext'
        ext_content = """\
    [ext]
    keyUsage = critical, digitalSignature, keyCertSign, keyEncipherment
    basicConstraints = critical, CA:TRUE
    """
            
        with open(ext_file_path, 'w') as ext_file:
            ext_file.write(ext_content)
            
            # Команда для создания CSR
        generate_server_csr_cmd = [
                'openssl', 'req', '-new', '-key', self.ECDSA_key,
                '-out', server_csr_path,
                '-subj', f'/C=RU/ST=Moscow/L=Moscow/O=AQSI/CN=AQSI_{self.selected_armi_number}-{self.selected_armi_number_number}'
            ]
            
            # Команда для подписания с использованием ext-файла
        sign_server_crt_cmd = [
                'openssl', 'x509', '-req', '-in', server_csr_path,
                '-CA', ca_crt_path, '-CAkey', ca_key_path,
                '-CAcreateserial', '-out', server_crt_path,
                '-days', str(self.time), '-sha256',
                '-extfile', ext_file_path, 
                '-extensions', 'ext'         
            ]
            
            # Выполняем команды
        subprocess.run(generate_server_csr_cmd, check=True)
        subprocess.run(sign_server_crt_cmd, check=True)

        self.folder_path = str(f"{self.keys_dir}\{self.folder_name}")
            
            # Удаляем временный файл (опционально)
            
        os.remove(ext_file_path)
            
        return f"Сертификат успешно создан и подписан корневым сертификатом, сохранен {server_crt_path}"