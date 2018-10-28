"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a GitHub account name, print info about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github})

    row = db_cursor.fetchone()

    if row == None:
        print("Student doesn't exist")
    else:
        print("Student: {} {}\nGitHub account: {}".format(row[0], row[1], row[2]))


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    QUERY = """
        INSERT INTO students (first_name, last_name, github)
        VALUES (:first_name, :last_name, :github)
        """

    db.session.execute(QUERY, {'first_name': first_name,
                               'last_name': last_name,
                               'github': github})

    db.session.commit()

    print("Successfully added student: {} {}".format(first_name, last_name))


def get_project_by_title(title):
    """Given a project title, print information about the project."""

    QUERY = """
        SELECT * FROM projects
        WHERE title = :title
        """

    db_cursor = db.session.execute(QUERY, {'title': title})

    row = db_cursor.fetchone()

    if row == None:
        print("Project doesn't exist")
    else:
        print("Project Title: {}\nProject Description: {}".format(row[1], row[2]))

def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""

    QUERY = """
        SELECT project_title, grade FROM grades
        WHERE project_title = :title
        AND student_github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github, 'title': title})

    result = db_cursor.fetchall()

    print("Grades for {} are {}".format(result[0][0], result[0][1]))


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""

    QUERY = """
        INSERT INTO grades (student_github, project_title, grade)
        VALUES (:github, :title, :grade)
        """

    db.session.execute(QUERY, {'github': github,
                               'title' : title,
                               'grade' : grade})

    db.session.commit()

    print("Successfully added grade {} to {}".format(grade, github))

def add_project(title, description, maximum_grade):
    """ Adds a new project to the projects table."""

    QUERY = """
        INSERT INTO projects (title, description, max_grade)
        VALUES (:title, :description, :maximum_grade)
        """
    db.session.execute(QUERY, {'title'         : title,
                               'description'   : description,
                               'maximum_grade' : maximum_grade})

    db.session.commit()

    print("Successfully added new project: {}".format(title))

def get_all_grades(github):
    """ get all grades."""

    QUERY = """
        SELECT project_title, grade FROM grades
        WHERE student_github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github})

    result = db_cursor.fetchall()

    if len(result) == 0:
        print("Student does not exist.")
    else:
        print("Grades for {} are".format(github))
        for item in result:
            print(str(item[0]) + " : " + str(item[1]))

def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received
    as a command.
    """

    command = None

    while command != "quit":
        input_string = input("HBA Database> ")
        tokens = input_string.split("|")
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args  # unpack!
            make_new_student(first_name, last_name, github)

        elif command == "title":
            title = " ".join(args)
            get_project_by_title(title)

        elif command == "grade":
            github = args[0]
            project = args[1]
            get_grade_by_github_title(github, project)

        elif command == "assign":
            title = args[1]
            github = args[0]
            grade = args[2]
            assign_grade(github, title, grade)

        elif command == "project":
            title = args[0]
            description = args[1]
            max_grade = args[2]
            add_project(title, description, max_grade)

        elif command == 'get':
            github = args[0]
            get_all_grades(github)

        else:
            if command != "quit":
                print("Invalid Entry. Try again.")


if __name__ == "__main__":
    connect_to_db(app)

    handle_input()

    # To be tidy, we close our database connection -- though,
    # since this is where our program ends, we'd quit anyway.

    db.session.close()
