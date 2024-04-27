from flask import Flask, redirect, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime, timedelta
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "assignment.db"
)
db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    major = db.Column(db.String(100), nullable=True)
    year = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return "<Student %r>" % self.name


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey("professor.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    student = db.relationship("Student", backref="assignments")
    professor = db.relationship("Professor", backref="assignments")

    def __repr__(self):
        return "<Assignment %r>" % self.name


class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "<Professor %r>" % self.name


class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    assignment_id = db.Column(
        db.Integer, db.ForeignKey("assignment.id"), nullable=False
    )
    grade = db.Column(db.Float, nullable=True)

    student = db.relationship("Student", backref="grades_received")
    assignment = db.relationship("Assignment", backref="grades")

    def __repr__(self):
        return f"<Grade id={self.id}, student_id={self.student_id}, assignment_id={self.assignment_id}, grade={self.grade}>"


class Student_Assignments(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), primary_key=True)
    assignment_id = db.Column(
        db.Integer, db.ForeignKey("assignment.id"), primary_key=True
    )
    status = db.Column(db.String(50), nullable=False)

    student = db.relationship(
        "Student", backref=db.backref("assigned_assignments", cascade="all,delete")
    )
    assignment = db.relationship(
        "Assignment", backref=db.backref("assigned_students", cascade="all,delete")
    )

    def __repr__(self):
        return f"<Student_Assignments student_id={self.student_id}, assignment_id={self.assignment_id}, status={self.status}>"


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    # completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Task %r>" % self.id


@app.route("/", methods=["POST", "GET"])
def index():  # define route
    if request.method == "POST":
        action = request.form.get("action")
        if action == "addStudent":
            student_name = request.form["studentName"]
            student_email = request.form["studentEmail"]
            student_major = request.form["studentMajor"]
            student_year = request.form["studentYear"]

            new_student = Student(
                name=student_name,
                email=student_email,
                major=student_major,
                year=student_year,
            )
            try:
                db.session.add(new_student)
                db.session.commit()
                return redirect("/")
            except:
                return "Error adding student"
        elif action == "addProfessor":
            professor_name = request.form["professorName"]
            professor_email = request.form["professorEmail"]
            professor_department = request.form["professorDepartment"]

            new_professor = Professor(
                name=professor_name,
                email=professor_email,
                department=professor_department,
            )
            try:
                db.session.add(new_professor)
                db.session.commit()
                return redirect("/")
            except:
                return "Error adding professor"
        elif action == "addAssignment":
            assignment_name = request.form["assignmentName"]
            assignment_description = request.form["assignmentDescription"]
            assignment_due_date_str = request.form["assignmentDueDate"]
            assignment_professor_id = request.form["assignmentProfessorId"]
            assignment_student_id = request.form["assignmentStudentId"]

            assignment_due_date = datetime.strptime(assignment_due_date_str, "%Y-%m-%d")

            # Create the assignment
            new_assignment = Assignment(
                name=assignment_name,
                description=assignment_description,
                due_date=assignment_due_date,
                professor_id=assignment_professor_id,
                student_id=assignment_student_id,
            )

            try:
                db.session.add(new_assignment)
                db.session.commit()

                new_student_assignment = Student_Assignments(
                    student_id=assignment_student_id,
                    assignment_id=new_assignment.id,
                    status="In Progress",
                )

                db.session.add(new_student_assignment)
                db.session.commit()

                new_grade = Grades(
                    student_id=assignment_student_id,
                    assignment_id=new_assignment.id,
                    grade="-1",
                )

                db.session.add(new_grade)
                db.session.commit()

                return redirect("/")
            except Exception as e:
                return "Error adding assignment" + str(e)
    else:
        students = Student.query.order_by(Student.name).all()
        professors = Professor.query.order_by(Professor.name).all()
        assignments = Assignment.query.order_by(Assignment.due_date).all()
        grades = Grades.query.all()
        return render_template(
            "index.html",
            assignments=assignments,
            professors=professors,
            students=students,
            grades=grades,
        )


@app.route("/report/student/<int:id>")
def report_student(id):
    student = Student.query.get_or_404(id)
    completed_only = request.args.get("completedOnly") == "true"  # Get query parameter

    if completed_only:
        assignments = (
            Assignment.query.filter_by(student_id=id)
            .join(Grades)
            .filter(Grades.grade >= 0)
            .all()
        )  # Only those with a valid grade
    else:
        assignments = Assignment.query.filter_by(student_id=id).all()

    student_grades = Grades.query.filter_by(student_id=id).all()

    # Create a dictionary to map assignment ID to its grade
    assignment_grades = {grade.assignment_id: grade.grade for grade in student_grades}

    return render_template(
        "reportStudent.html",
        student=student,
        assignments=assignments,
        assignment_grades=assignment_grades,
    )


@app.route("/report/professor/<int:id>")
def report_professor(id):
    with db.engine.connect() as conn:
        # Fetch the professor by ID
        professor_stmt = text("SELECT * FROM professor WHERE id = :professor_id")
        professor_result = conn.execute(professor_stmt, {"professor_id": id})
        professor = professor_result.mappings().one()  # Fetch as dictionary

        # Fetch all assignments for the professor
        assignments_stmt = text(
            """
            SELECT 
                assignment.id,
                assignment.name,
                assignment.description,
                assignment.due_date
            FROM 
                assignment
            WHERE 
                assignment.professor_id = :professor_id
            """
        )
        assignments_result = conn.execute(assignments_stmt, {"professor_id": id})
        assignments = (
            assignments_result.mappings().all()
        )  # Fetch all assignments as dictionaries

        # Determine if "completed only" filter is checked
        completed_only = request.args.get("completedOnly") == "true"
        if completed_only:
            # Fetch grades for these assignments
            grades_stmt = text(
                """
                SELECT 
                    assignment_id, 
                    grade
                FROM 
                    grades
                WHERE 
                    assignment_id IN (
                        SELECT id FROM assignment WHERE professor_id = :professor_id
                    )
                """
            )
            grades_result = conn.execute(grades_stmt, {"professor_id": id})
            grades = {
                g["assignment_id"]: g["grade"] for g in grades_result.mappings().all()
            }

            # Filter assignments based on completed grades
            assignments = [a for a in assignments if grades.get(a["id"], -1) >= 0]

    # Render the report
    return render_template(
        "reportProfessor.html", professor=professor, assignments=assignments
    )


# def report_professor(id):
#     # Fetch the professor by ID
#     professor = Professor.query.get_or_404(id)

#     # Fetch all assignments for this professor
#     assignments = Assignment.query.filter_by(professor_id=id).all()

#     # If "completed only" is checked, filter assignments that are completed
#     completed_only = request.args.get("completedOnly") == "true"  # Get query parameter
#     if completed_only:
#         # Assuming assignments have a status field to indicate if they are completed
#         assignments = [
#             a for a in assignments if any(grade.grade != -1 for grade in a.grades)
#         ]

#     return render_template(
#         "reportProfessor.html", professor=professor, assignments=assignments
#     )


app.route("/report/student/<int:id>")


def report_student(id):
    with db.engine.connect() as conn:
        # Get the "completed only" filter from the request
        completed_only = request.args.get("completedOnly") == "true"

        # Base SQL query to fetch student details
        student_stmt = text("SELECT * FROM student WHERE id = :student_id")

        # Fetch student details
        student_result = conn.execute(student_stmt, {"student_id": id})
        student = student_result.mappings().one()  # Get a single result as a dictionary

        # Construct SQL statement based on the completed_only filter
        if completed_only:
            assignment_stmt = text(
                """
                SELECT 
                    assignment.id, 
                    assignment.name, 
                    assignment.description, 
                    assignment.due_date,
                    grades.grade
                FROM 
                    assignment
                JOIN 
                    grades 
                ON 
                    assignment.id = grades.assignment_id
                WHERE 
                    assignment.student_id = :student_id
                    AND grades.grade >= 0
                """
            )
        else:
            assignment_stmt = text(
                """
                SELECT 
                    assignment.id, 
                    assignment.name, 
                    assignment.description,
                    assignment.due_date
                FROM 
                    assignment
                WHERE 
                    assignment.student_id = :student_id
                """
            )

        # Fetch the assignments and related grades
        assignments_result = conn.execute(assignment_stmt, {"student_id": id})
        assignments = (
            assignments_result.mappings().all()
        )  # Get all assignments as dictionaries

        # Map assignment IDs to their grades
        assignment_grades = {
            assignment["id"]: assignment.get("grade", -1) for assignment in assignments
        }

    # Render the template with the retrieved data
    return render_template(
        "reportStudent.html",
        student=student,
        assignments=assignments,
        assignment_grades=assignment_grades,
    )


@app.route("/report/avgGrade/", methods=["GET"])
def reportAvgGrade():
    with db.engine.connect() as conn:
        stmt = text(
            """
        SELECT 
            student.name, 
            AVG(grades.grade) as average_grade
        FROM 
            student
        JOIN 
            grades 
        ON 
            student.id = grades.student_id
        WHERE 
            grades.grade >= 0
        GROUP BY 
            student.id
        """
        )

        result = conn.execute(stmt.execution_options(result_set_keyed=True))
        result_rows = result.fetchall()  # Get all rows from the result

        avg_grades = [{"name": row[0], "average_grade": row[1]} for row in result_rows]

    return render_template("reportAvgGrade.html", avg_grades=avg_grades)


@app.route("/report/dueSoon/", methods=["GET"])
def report_due_soon():
    with db.engine.connect() as conn:
        # Calculate the date one week from today
        due_soon_date = datetime.now() + timedelta(days=7)

        # Create a prepared SQL statement to fetch assignments due within the next 7 days
        stmt = text(
            """
            SELECT
                assignment.name,
                assignment.description,
                assignment.due_date,
                student.name AS student_name
            FROM
                assignment
            JOIN
                student
            ON
                assignment.student_id = student.id
            WHERE
                assignment.due_date <= :due_soon_date
            """
        )

        # Execute the SQL statement with a parameter
        result = conn.execute(stmt, {"due_soon_date": due_soon_date})

        # Retrieve the results as a list of dictionaries
        assignments_due_soon = result.mappings().all()

    # Render the report with the fetched data
    return render_template(
        "reportDueSoon.html", assignments_due_soon=assignments_due_soon
    )


@app.route("/report/avgGradeByProfessor/", methods=["GET"])
def report_avg_grade_by_professor():
    with db.engine.connect() as conn:
        # Prepare a SQL statement to calculate the average grade by professor
        stmt = text(
            """
            SELECT
                professor.name AS professor_name,
                AVG(grades.grade) AS average_grade
            FROM
                professor
            JOIN
                assignment
            ON
                professor.id = assignment.professor_id
            JOIN
                grades
            ON
                assignment.id = grades.assignment_id
            WHERE 
                grades.grade >= 0
            GROUP BY
                professor.id
            """
        )

        # Execute the SQL statement and get the results
        result = conn.execute(stmt)

        # Retrieve the results as a list of dictionaries for rendering
        professor_grades = result.mappings().all()

    # Render the report with the fetched data
    return render_template(
        "reportAvgGradeByProfessor.html", professor_grades=professor_grades
    )


@app.route("/delete/student/<int:id>")
def deleteStudent(id):
    student = Student.query.get_or_404(id)

    try:
        # Cascade delete
        Student_Assignments.query.filter_by(student_id=id).delete()
        Assignment.query.filter_by(student_id=id).delete()
        Grades.query.filter_by(student_id=id).delete()

        db.session.delete(student)
        db.session.commit()
        return redirect("/")
    except:
        return "Error deleting assignment"


@app.route("/delete/professor/<int:id>")
def deleteProfessor(id):
    professor = Professor.query.get_or_404(id)

    try:
        # Delete all professor instances in assignment table
        Assignment.query.filter_by(professor_id=id).delete()

        db.session.delete(professor)
        db.session.commit()
        return redirect("/")
    except:
        return "Error deleting professor"


@app.route("/delete/assignment/<int:id>")
def deleteAssignment(id):
    assignment = Assignment.query.get_or_404(id)

    try:
        # Cascade delete grade
        grade_delete = Grades.query.filter_by(assignment_id=id).all()
        for grade in grade_delete:
            db.session.delete(grade)

        student_assignment_delete = Student_Assignments.query.filter_by(
            assignment_id=id
        ).all()
        for student in student_assignment_delete:
            db.session.delete(student)

        db.session.delete(assignment)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return "Error deleting assingmetn" + str(e)


@app.route("/addGrade/<int:id>", methods=["GET", "POST"])
def addGrade(id):
    grade = Grades.query.get_or_404(id)

    if request.method == "POST":
        grade.grade = request.form["gradeValue"]

        try:
            db.session.add(grade)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return "Error adding grade" + str(e)
    else:
        return render_template("addGrade.html", grade=grade)


@app.route("/update/assignment/<int:id>", methods=["GET", "POST"])
def updateAssignment(id):
    assignment = Assignment.query.get_or_404(id)
    professors = Professor.query.all()
    students = Student.query.all()

    if request.method == "POST":
        assignment.name = request.form["assignmentName"]
        assignment.description = request.form["assignmentDescription"]
        assignment.due_date = datetime.strptime(
            request.form["assignmentDueDate"], "%Y-%m-%d"
        )
        assignment.professor_id = request.form["assignmentProfessorId"]
        assignment.student_id = request.form["assignmentStudentId"]

        try:
            db.session.commit()
            return redirect("/")
        except:
            return "Error updating assignment"
    else:
        return render_template(
            "updateAssignment.html",
            professors=professors,
            students=students,
            assignment=assignment,
        )


@app.route("/update/professor/<int:id>", methods=["GET", "POST"])
def updateProfessor(id):
    professor = Professor.query.get_or_404(id)

    if request.method == "POST":
        professor.name = request.form["professorName"]
        professor.email = request.form["professorEmail"]
        professor.department = request.form["professorDepartment"]

        try:
            db.session.commit()
            return redirect("/")
        except:
            return "Error updating professor"
    else:
        return render_template("updateProfessor.html", professor=professor)


@app.route("/update/student/<int:id>", methods=["GET", "POST"])
def updateStudent(id):
    student = Student.query.get_or_404(id)

    if request.method == "POST":
        student.name = request.form["studentName"]
        student.email = request.form["studentEmail"]
        student.major = request.form["studentMajor"]
        student.year = request.form["studentYear"]

        try:
            db.session.commit()
            return redirect("/")
        except:
            return "Error updating student"
    else:
        return render_template("updateStudent.html", student=student)


if __name__ == "__main__":
    app.run(debug=True)
