import sys
import dateutil.parser as dparser
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication, QLineEdit, QMainWindow, QMessageBox
from sqlalchemy import (Column, Date, ForeignKey, Table,
                        create_engine, insert, select)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

import issue_ui

Base = automap_base()
engine = create_engine("mysql://vedant:vedant@localhost/library_management")
t_issues = Table(
    'issues', Base.metadata,
    Column('book_no', ForeignKey('books.Acc_no', ondelete='CASCADE', onupdate='CASCADE'), index=True, comment='The Accession number of the book issued'),
    Column('student_id', ForeignKey('students.Admno', ondelete='CASCADE', onupdate='CASCADE'), index=True, comment='The Admission Number of the student who is issuing the book'),
    Column('issue_date', Date, comment='The date of issuing the book'),
    Column('return_date', Date, comment='The date of returning the book'),
    comment='A table for storing info of issued books'
)
Base.prepare(engine, reflect=True)
Book = Base.classes.books
Student = Base.classes.students


session = Session(engine)


class Issue(QMainWindow, issue_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.issue_date.setDate(QDate.currentDate())
        self.ret_date.setDate(QDate.currentDate().addDays(6))
        self.issue_book.clicked.connect(self.issue)

    def issue(self):
        student_id = int(self.stu_no.text())
        book_id = self.book_no.text()

        # Validate Student
        statement = select(Student).filter_by(Admno=student_id)
        result = session.execute(statement).scalars().all()
        if not result:
            error = QMessageBox()
            error.setStandardButtons(QMessageBox.StandardButton.Ok)
            error.setWindowTitle("Student Not Found")
            error.setText(f"The Student with Admission Number {student_id} is not present in the school")
            error.setIcon(QMessageBox.Icon.Critical)
            error = error.exec()
            if error == QMessageBox.StandardButton.Ok:
                for widget in self.findChildren(QLineEdit):
                    widget.clear()
        else:
            # Validate Book
            statement = select(Book).filter_by(Acc_no=book_id)
            result = session.execute(statement).scalars().all()
            if not result:
                error = QMessageBox()
                error.setStandardButtons(QMessageBox.StandardButton.Ok)
                error.setWindowTitle("Book Not Found")
                error.setText(f"The book with book number {book_id} is not present in the library")
                error.setIcon(QMessageBox.Icon.Critical)
                error = error.exec()
                if error == QMessageBox.StandardButton.Ok:
                    for widget in self.findChildren(QLineEdit):
                        widget.clear()
            else:
                # Validate If Issued
                statement = select(t_issues).filter_by(book_no=book_id)
                result = session.execute(statement)
                if result:
                    error = QMessageBox()
                    error.setStandardButtons(QMessageBox.StandardButton.Ok)
                    error.setWindowTitle("Book Not Found")
                    error.setText(f"The book with book number {book_id} is already issued")
                    error.setIcon(QMessageBox.Icon.Critical)
                    error = error.exec()
                    if error == QMessageBox.StandardButton.Ok:
                        for widget in self.findChildren(QLineEdit):
                            widget.clear()
                else:
                    iss_date = dparser.parse(
                        self.issue_date.text(), fuzzy=True, ignoretz=True).date()
                    return_date = dparser.parse(
                        self.issue_date.text(), fuzzy=True, ignoretz=True).date()
                    self.submit(book_id, student_id, iss_date, return_date)


    def submit(self, book_id, student_id, iss_date, return_date):
                try:
                    stmt = insert(t_issues).values(
                        book_no=book_id, student_id=student_id, issue_date=iss_date, return_date=return_date)
                    session.execute(stmt)
                    session.commit()
                    success = QMessageBox()
                    success.setText("Book Issued")
                    success.setWindowTitle("Successful")
                    success.setIcon(QMessageBox.Icon.Information)
                    success.setStandardButtons(QMessageBox.StandardButton.Ok)
                    success = success.exec()
                    if success == QMessageBox.StandardButton.Ok:
                        for widget in self.findChildren(QLineEdit):
                            widget.clear()
                except IntegrityError:
                    session.rollback()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Issue()
    win.show()
    sys.exit(app.exec())
