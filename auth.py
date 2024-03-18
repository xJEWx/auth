# Импорт необходимых модулей

# Модуль os предоставляет функционал для взаимодействия с операционной системой, в данном случае, используется для работы с файловой системой.
import os
# Модуль hashlib предоставляет безопасные хеш-функции, используется для хеширования паролей.
import hashlib
# Модуль logging предоставляет гибкие средства ведения журнала, используется для записи информации о событиях в программе.
import logging
# Модуль secrets предоставляет функции для генерации криптографически безопасных случайных чисел и строк, используется для генерации соли.
import secrets
# Модуль time предоставляет функции для работы со временем, используется для определения времени блокировки учетной записи.
import time
# Модуль webbrowser предоставляет интерфейс для открытия веб-браузера, используется для открытия URL-адресов после успешной аутентификации.
import webbrowser
# Модуль tkinter предоставляет инструментарий для создания графического пользовательского интерфейса (GUI) в Tkinter.
from tkinter import Tk, Label, Entry, Button, messagebox, Toplevel

# Определение путей к директории и файлам
credentials_directory = "C:\\authentication"
credentials_file_path = os.path.join(credentials_directory, "credentials.txt")
log_file_path = os.path.join(credentials_directory, "auth_log.txt")

# Обеспечение существования директории и создание файлов, если их нет
if not os.path.exists(credentials_directory):
    os.makedirs(credentials_directory)

if not os.path.exists(log_file_path):
    with open(log_file_path, 'w'):
        pass

# Настройка системы логирования
logging.basicConfig(filename=log_file_path, level=logging.INFO,\
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация переменных для попыток входа и времени блокировки
login_attempts = 0
blocked_time = 0

# Функция создания исходного файла с учетными данными
def create_credentials_file():
    with open(credentials_file_path, 'w') as file:
        file.write("admin:3a22f811d6ea6516:21f996fd022cc04ea57fca95e7bb3e2a\n")

# Функция загрузки учетных данных из файла
def load_credentials():
    credentials = {}
    try:
        with open(credentials_file_path, 'r') as file:
            for line in file:
                username, salt, hashed_password = line.strip().split(':')
                credentials[username] = (salt, hashed_password)
    except FileNotFoundError:
        create_credentials_file()
    return credentials

# Функция сохранения учетных данных в файл
def save_credentials(credentials):
    with open(credentials_file_path, 'w') as file:
        for username, (salt, hashed_password) in credentials.items():
            file.write(f"{username}:{salt}:{hashed_password}\n")

# Функция для записи активности пользователя в журнал
def log_activity(username, action):
    logging.info(f"Пользователь {username} {action}")

# Функция открытия окна регистрации пользователя
def register_user_window():
    register_window = Toplevel(root)
    register_window.title("Регистрация")

    label_username = Label(register_window, text="Логин:")
    label_username.grid(row=0, column=0, padx=10, pady=10)

    entry_username = Entry(register_window)
    entry_username.grid(row=0, column=1, padx=10, pady=10)

    label_password = Label(register_window, text="Пароль:")
    label_password.grid(row=1, column=0, padx=10, pady=10)

    entry_password = Entry(register_window, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=10)

    button_register = Button(register_window, text="Зарегистрировать", command=lambda: register_user(entry_username.get(), entry_password.get(), register_window))
    button_register.grid(row=2, column=0, columnspan=2, pady=10)

# Функция для регистрации нового пользователя
def register_user(username, password, register_window):
    credentials = load_credentials()

    if username in credentials:
        messagebox.showerror("Ошибка", f"Пользователь {username} уже существует.")
    else:
        salt = secrets.token_hex(8)
        hashed_password = hashlib.md5((password + salt).encode()).hexdigest()
        credentials[username] = (salt, hashed_password)
        save_credentials(credentials)
        messagebox.showinfo("Успех", f"Пользователь {username} успешно зарегистрирован.")
        log_activity(username, "зарегистрирован")
        register_window.destroy()

# Функция для аутентификации пользователя
def authenticate_user():
    global login_attempts, blocked_time
    username = entry_username.get()
    password = entry_password.get()

    # Проверка блокировки учетной записи
    if time.time() < blocked_time:
        messagebox.showerror("Ошибка", "Учетная запись заблокирована. Попробуйте позже.")
        return

    credentials = load_credentials()

    if username in credentials:
        salt, hashed_password = credentials[username]
        hashed_password_input = hashlib.md5((password + salt).encode()).hexdigest()

        # Проверка, является ли пользователь администратором
        if username == "admin" and hashed_password_input == hashed_password:
            messagebox.showinfo("Успех", f"Пользователь {username} успешно аутентифицирован.")
            log_activity(username, "вошел в систему")
            login_attempts = 0
            webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        # Проверка, является ли пользователь обычным пользователем
        elif hashed_password == hashed_password_input:
            messagebox.showinfo("Успех", f"Пользователь {username} успешно аутентифицирован.")
            log_activity(username, "вошел в систему")
            login_attempts = 0
            webbrowser.open("https://itmo.ru/news")
        else:
            messagebox.showerror("Ошибка", "Неверный пароль.")
            login_attempts += 1

            # Блокировка учетной записи при превышении 5 попыток входа
            if login_attempts >= 5:
                blocked_time = time.time() + 10
                log_activity(username, "учетная запись заблокирована")
                messagebox.showerror("Ошибка", "Превышено количество попыток. Учетная запись заблокирована на 10 секунд.")
    else:
        messagebox.showerror("Ошибка", "Пользователь не найден.")

# Создание главного окна Tkinter
root = Tk()
root.title("Аутентификация")

# Создание и размещение меток, полей ввода и кнопок в главном окне
label_username = Label(root, text="Логин:")
label_username.grid(row=0, column=0, padx=10, pady=10)

entry_username = Entry(root)
entry_username.grid(row=0, column=1, padx=10, pady=10)

label_password = Label(root, text="Пароль:")
label_password.grid(row=1, column=0, padx=10, pady=10)

entry_password = Entry(root, show="*")
entry_password.grid(row=1, column=1, padx=10, pady=10)

button_register = Button(root, text="Регистрация", command=register_user_window)
button_register.grid(row=2, column=0, pady=10)

button_authenticate = Button(root, text="Аутентифицировать", command=authenticate_user)
button_authenticate.grid(row=2, column=1, pady=10)

# Запуск основного цикла событий Tkinter
root.mainloop()