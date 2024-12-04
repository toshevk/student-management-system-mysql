from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QLineEdit, QPushButton, QMainWindow,\
     QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QSize
import sys
import sqlite3
import pandas as pd
import mysql.connector


class MainWindow(QMainWindow):
    def __init__(self):
        self.database = Database()
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(QSize(800, 600))

        # Add menu items
        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        # File menu action
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # Edit menu action
        search_action = QAction(QIcon("icons/search.png"), "Search Student", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about_message)
        help_menu_item.addAction(about_action)
        # If app is run on Mac enable this line
        # to display last item of menu bar
        #
        # about_action.setMenuRole(QAction.MenuRole.NoRole)

        # Create toolbar and toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create main table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create status bar and status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        # Create Status bar elements
        edit_btn_status = QPushButton("Edit Record")
        edit_btn_status.clicked.connect(self.edit)

        delete_btn_status = QPushButton("Delete Record")
        delete_btn_status.clicked.connect(self.delete)

        # Clear status bar from previous buttons
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_btn_status)
        self.statusbar.addWidget(delete_btn_status)

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def load_data(self):
        connection = self.database.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        response = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(response):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        cursor.close()
        connection.close()

    def load_course_list(self):
        course_list = df["course name"].values.tolist()
        return course_list

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchStudentDialog()
        dialog.exec()

    def about_message(self):
        content = """
        Made by Krste Toshev.\n
        \n
        For help or advanced instructions,\n
        contact us on e-mail:\n
        toshev.krste@yahoo.com
        """
        message = QMessageBox()
        message.setText(content)
        message.setWindowTitle("About Us")
        message.setContentsMargins(0, 10, 50, 10)
        message.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course = QComboBox()
        courses = student_management_system.load_course_list()
        self.course.addItems(courses)
        layout.addWidget(self.course)

        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile Phone")
        layout.addWidget(self.mobile)

        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course.itemText(self.course.currentIndex())
        mobile = self.mobile.text()
        connection = student_management_system.database.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)", (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        student_management_system.load_data()


class SearchStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        layout = QVBoxLayout()

        self.search_query = QLineEdit()
        layout.addWidget(self.search_query)

        search_button = QPushButton("Search")
        layout.addWidget(search_button)
        search_button.clicked.connect(self.search)

        self.setLayout(layout)

    def search(self):
        query = str(self.search_query.text())
        connection = student_management_system.database.connect()
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM students WHERE name LIKE %s", (query, ))
        response = cursor.fetchall()
        occurrences = student_management_system.table.findItems(query, Qt.MatchFlag.MatchContains)
        for occurrence in occurrences:
            student_management_system.table.item(occurrence.row(), 1).setSelected(True)
        cursor.close()
        connection.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        window_size = QSize(300, 300)
        self.setFixedSize(window_size)

        layout = QVBoxLayout()

        row_index = student_management_system.table.currentRow()
        current_student_name = student_management_system.table.item(row_index, 1).text()
        self.selected_student_id = student_management_system.table.item(row_index, 0).text()

        self.student_name = QLineEdit(f"{current_student_name}")
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        current_course_name = student_management_system.table.item(row_index, 2).text()
        self.course = QComboBox()
        courses = student_management_system.load_course_list()
        self.course.addItems(courses)
        self.course.setCurrentText(current_course_name)
        layout.addWidget(self.course)

        current_student_phone = student_management_system.table.item(row_index, 3).text()
        self.mobile = QLineEdit(f"{current_student_phone}")
        self.mobile.setPlaceholderText("Mobile Phone")
        layout.addWidget(self.mobile)

        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = student_management_system.database.connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                       (self.student_name.text(), self.course.currentText(), self.mobile.text(),
                        self.selected_student_id))
        connection.commit()
        cursor.close()
        connection.close()
        # Refresh main window table
        student_management_system.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Record")
        layout = QGridLayout()

        delete_label = QLabel("Are you sure you want to delete this record?")
        layout.addWidget(delete_label, 0, 0, 1, 2)

        row_index = student_management_system.table.currentRow()
        delete_record_name = student_management_system.table.item(row_index, 1).text()
        delete_record_phone = student_management_system.table.item(row_index, 3).text()
        delete_record_label = QLabel(f"{delete_record_name}\n"
                                     f"{delete_record_phone}")
        layout.addWidget(delete_record_label, 1, 0, 1, 2)

        delete_btn = QPushButton("Delete")
        cancel_btn = QPushButton("Cancel")
        delete_btn.clicked.connect(self.delete_record)
        cancel_btn.clicked.connect(self.close)
        layout.addWidget(delete_btn, 2, 0)
        layout.addWidget(cancel_btn, 2, 1)

        self.setLayout(layout)

    def delete_record(self):
        row_index = student_management_system.table.currentRow()
        delete_index = int(student_management_system.table.item(row_index, 0).text())
        delete_name = student_management_system.table.item(row_index, 1).text()
        delete_phone = student_management_system.table.item(row_index, 3).text()

        connection = student_management_system.database.connect()
        cursor = connection.cursor()
        # delete_record = cursor.execute(f"SELECT * FROM students WHERE name LIKE '%{delete_name}%' AND mobile LIKE {delete_phone}").fetchall()
        # delete_record_id = delete_record[0][0]
        cursor.execute("DELETE FROM students WHERE id = %s", (delete_index, ))
        cursor.close()
        connection.commit()
        connection.close()

        student_management_system.load_data()
        self.close()

        deletion_confirmation_message = QMessageBox()
        deletion_confirmation_message.setWindowTitle("Deleted")
        deletion_confirmation_message.setText(f"Record {delete_name} was deleted successfully!")
        deletion_confirmation_message.exec()


class Database:
    # Initialize database connection
    def __init__(self, host="localhost", user="root", password="malemale123", database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password, database=self.database)
        return connection


# Load course list
df = pd.read_csv("courses.csv")
# Initiate app
app = QApplication(sys.argv)
student_management_system = MainWindow()
student_management_system.show()
# Load database data
student_management_system.load_data()
database = Database()
sys.exit(app.exec())
