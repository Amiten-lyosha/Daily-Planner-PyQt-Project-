from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QListWidgetItem, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
import sqlite3
import sys


class Welcome(QDialog):
    def __init__(self):
        super(Welcome, self).__init__()
        loadUi("Welcome.ui", self)
        self.login.clicked.connect(self.tologin)
        self.create.clicked.connect(self.tocreate)

    def tologin(self):
        login = LoginScreen()
        window.addWidget(login)
        window.setCurrentIndex(window.currentIndex() + 1)

    def tocreate(self):
        create = CreateScreen()
        window.addWidget(create)
        window.setCurrentIndex(window.currentIndex() + 1)


class LoginScreen(QDialog):   # виджет входа
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui", self)
        self.linePassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(lambda: self.loginfunc())

    def loginfunc(self):
        user = self.lineName.text()
        passw = self.linePassword.text()
        if len(user) == 0 and len(passw) == 0:
            self.error.setText("Введите данные.")
        else:
            conn = sqlite3.connect("profile.db")
            curs = conn.cursor()
            query1 = 'SELECT password FROM login_info WHERE username =\''+user+"\'"
            curs.execute(query1)
            result_pass = curs.fetchone()[0]
            if result_pass == passw:
                print("Успешно!")
                self.error.setText("")

                calendar = Window()
                window.addWidget(calendar)
                window.setCurrentIndex(window.currentIndex() + 1)
            else:
                print("Ошибка. Неверно введён пароль или имя пользователя.")


class CreateScreen(QDialog):   # виджет регистрации
    def __init__(self):
        super(CreateScreen, self).__init__()
        loadUi("createacc.ui", self)
        self.linePassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(lambda: self.signupfunc())

    def signupfunc(self):
        user = self.lineName.text()
        passw = self.linePassword.text()
        confirmpassw = self.lineConfPassword.text()
        if len(user) == 0 or len(passw) == 0 or len(confirmpassw) == 0:
            self.error.setText("Ну как так то! Заполни поля ёмаё...")
        elif passw != confirmpassw:
            self.error.setText("Ну как так то! Пароль и подтверждение не совпадают.")
        else:
            conn = sqlite3.connect("profile.db")
            cur = conn.cursor()

            user_info = [user, passw]
            cur.execute('INSERT INTO login_info (username, password) VALUES (?,?)', user_info)

            conn.commit()
            conn.close()

            calendar = Window()
            window.addWidget(calendar)
            window.setCurrentIndex(window.currentIndex()+1)


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        loadUi("Calendar.ui", self)  # загружаем ui для последующей работы
        self.saveButton.clicked.connect(self.saveChangesTasks)  # подключение кнопок
        self.addButton.clicked.connect(self.addNewTask)
        self.db = sqlite3.connect("data.db")    # обращаемся к базе данных
        self.cursor = self.db.cursor()  # создаём курсор
        self.date = self.calendarWidget.selectedDate().toPyDate()

    def updateTaskList(self, date):
        self.tasksListWidget.clear()
        query = "SELECT task, completed FROM tasks WHERE date = ?"
        row = (date,)
        results = self.cursor.execute(query, row).fetchall()
        # добавляем задачи в лист виджет
        for result in results:
            item = QListWidgetItem(str(result[0]))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if result[1] == "YES":
                item.setCheckState(Qt.Checked)
            elif result[1] == "NO":
                item.setCheckState(Qt.Unchecked)
            self.tasksListWidget.addItem(item)

    def saveChangesTasks(self):     # сохранение списка задач (# по-моему здесь всё итак понятно ;))
        date = self.calendarWidget.selectedDate().toPyDate()
        for i in range(self.tasksListWidget.count()):
            item = self.tasksListWidget.item(i)
            task = item.text()
            if item.checkState() == Qt.Checked:
                query = "UPDATE tasks SET completed = 'YES' WHERE task = ? AND date = ?"
            else:
                query = "UPDATE tasks SET completed = 'NO' WHERE task = ? AND date = ?"
            row = (task, date,)
            self.cursor.execute(query, row)
            self.db.commit()
            message_box = QMessageBox()
            message_box.setText("Изменено.")    # выводит окно об изменении
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec()

    def addNewTask(self):   # создание задачи
        new_task = str(self.lineEdit.text())
        date = self.calendarWidget.selectedDate().toPyDate()
        query = "INSERT INTO tasks(task, completed, date) VALUES (?,?,?)"
        row = (new_task, "NO", date,)
        self.cursor.execute(query, row)
        self.db.commit()
        self.updateTaskList(date)
        self.lineEdit.clear()


app = QApplication(sys.argv)
welcome = Welcome()
window = QtWidgets.QStackedWidget()
window.addWidget(welcome)
window.setFixedHeight(590)
window.setFixedWidth(405)
window.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
