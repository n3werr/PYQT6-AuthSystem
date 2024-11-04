import sys
import sqlite3
import re
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QMessageBox


class Auth(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('auth.ui', self)
        self.setWindowTitle('Авторизация')

        self.loginBtn.clicked.connect(self.loginbtn)
        self.registerBtn.clicked.connect(self.regBtn)
        self.ErrorMsg.hide()
        self.PswdLine.setEchoMode(QLineEdit.EchoMode.Password)

    def loginbtn(self):
        mail = self.MailLine.text()
        password = self.PswdLine.text()
        if mail == '':
            self.ErrorMsg.show()
            self.ErrorMsg.setText("Введите почту")
            return
        if password == '':
            self.ErrorMsg.show()
            self.ErrorMsg.setText("Введите пароль")
            return
        result = self.login(mail, password)
        if result is True:
            self.ErrorMsg.show()
            self.ErrorMsg.setText("Успешно.")
        elif result is False:
            self.ErrorMsg.show()
            self.ErrorMsg.setText("Неверный пароль.")
        else:
            self.ErrorMsg.show()
            self.ErrorMsg.setText("Пользователь не найден.")

    def login(self, mail, password):
        con = sqlite3.connect("users.sqlite")
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE mail = ?", (mail,))
        user = cur.fetchone()

        if user is None:
            con.close()
            return None

        cur.execute("SELECT * FROM users WHERE mail = ? AND password = ?", (mail, password))
        user = cur.fetchone()

        con.close()

        if user:
            return True
        else:
            return False

    def regBtn(self):
        global mail
        global password
        
        mail = self.MailLine.text()
        password = self.PswdLine.text()

        if mail == '':
            self.ErrorMsg.show()
            self.ErrorMsg.setText("Введите почту")
            return
        if password == '':
            self.ErrorMsg.show()
            self.ErrorMsg.setText("Введите пароль")
            return
        
        if '@' not in mail or '.' not in mail:
            self.ErrorMsg.show()
            self.ErrorMsg.setText("Введите верную почту.")
            return
        
        if len(password) < 8:
            QMessageBox.warning(self, "Ошибка", 
                                "Пароль должен содержать минимум 8 символов.")
            return 
        
        if not re.search(r"[A-Z]", password):
            QMessageBox.warning(self, "Ошибка", 
                                "Пароль должен содержать хотя бы одну заглавную букву.")
            return

        if not re.search(r"[a-z]", password):
           QMessageBox.warning(self, "Ошибка", 
                               "Пароль должен содержать хотя бы одну строчную букву.")
           return

        if not re.search(r"[0-9]", password):
            QMessageBox.warning(self, "Ошибка", 
                                "Пароль должен содержать хотя бы одну цифру.")
            return
    
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            QMessageBox.warning(self, "Ошибка", 
                                "Пароль должен содержать хотя бы один специальный символ.")
            return

        if re.search(r"\s", password):
            QMessageBox.warning(self, "Ошибка", 
                                "Пароль не должен содержать пробелы.")
            return

        con = sqlite3.connect("users.sqlite")
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE mail = ?", (mail,))
        user = cur.fetchone()

        if user is None:
            self.open_register_form()
        else:
            self.ErrorMsg.show()
            self.ErrorMsg.setText("Почта уже используется.")
        
        con.close()

    def open_register_form(self):
        self.close()
        self.register_window = Register()
        self.register_window.show()

class Register(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('register.ui', self)
        self.setWindowTitle('Регистрация')
        self.ErrorMsg.hide()
        self.registerBtn.clicked.connect(self.register)
    
    def register(self):
        name = self.nameLine.text()
        surname = self.surnameLine.text()
        patronymic = self.patronymicLine.text()
        datebirth = self.dateLine.text()
        
        if name.isalpha() is False or surname.isalpha() is False or patronymic.isalpha() is False:
            self.ErrorMsg.show()
            self.ErrorMsg.setText("ФИО должно содержать только буквы.")
        else:
            self.adduser(name, surname, patronymic, datebirth, mail, password)
            self.success_message()

    def success_message(self):
        answer = QMessageBox.information(self, "Успех", 
                                         "Регистрация успешна! Вы можете войти в систему.", 
                                         QMessageBox.StandardButton.Ok)
        if answer == QMessageBox.StandardButton.Ok:
            self.close()
            self.open_window = Auth()
            self.open_window.show()


    def adduser(self, name, surname, patronymic, datebirth, mail, password):
        con = sqlite3.connect("users.sqlite")
        cur = con.cursor()
            
        cur.execute("INSERT INTO users (mail, password, name, surname, patronymic, datebirth) VALUES (?, ?, ?, ?, ?, ?)",
                        (mail, password, name, surname, patronymic, datebirth))
        con.commit()
        con.close()
        
    
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Auth()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
