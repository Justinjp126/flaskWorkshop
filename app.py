from flask import Flask, redirect, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "assignment.db")
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
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignment.id"), nullable=False)
    grade = db.Column(db.Float, nullable=True)

    student = db.relationship("Student", backref="grades_received")
    assignment = db.relationship("Assignment", backref="grades")

    def __repr__(self):
        return f"<Grade id={self.id}, student_id={self.student_id}, assignment_id={self.assignment_id}, grade={self.grade}>"

class Student_Assignments(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), primary_key=True)
    status = db.Column(db.String(50), nullable=False)

    student = db.relationship('Student', backref=db.backref('assigned_assignments', cascade='all,delete'))
    assignment = db.relationship('Assignment', backref=db.backref('assigned_students', cascade='all,delete'))

    def __repr__(self):
        return f"<Student_Assignments student_id={self.student_id}, assignment_id={self.assignment_id}, status={self.status}>"

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    # completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Task %r>" % self.id


@app.route("/", methods=['POST', 'GET'])
def index():  # define route
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'addStudent':
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
            assignment_name = request.form['assignmentName']
            assignment_description = request.form['assignmentDescription']
            assignment_due_date_str = request.form["assignmentDueDate"]
            assignment_professor_id = request.form['assignmentProfessorId']
            assignment_student_id= request.form["assignmentStudentId"]

            assignment_due_date = datetime.strptime(assignment_due_date_str, '%Y-%m-%d')

            # Create the assignment
            new_assignment = Assignment(
                name=assignment_name,
                description=assignment_description,
                due_date=assignment_due_date,
                professor_id=assignment_professor_id,
                student_id=assignment_student_id
            )

            try:
                db.session.add(new_assignment)
                db.session.commit()

                new_student_assignment = Student_Assignments (
                    student_id=assignment_student_id,
                    assignment_id=new_assignment.id,
                    status="In Progress"
                )
                db.session.add(new_student_assignment)
                db.session.commit()

                new_grade = Grades (
                    student_id=assignment_student_id,
                    assignment_id=new_assignment.id,
                    grade=-1
                )

                db.session.add(new_grade)
                db.session.commit()

                return redirect('/')
            except Exception as e:
                return "Error adding assignment" + str(e)
    else:
        students = Student.query.order_by(Student.name).all()
        professors = Professor.query.order_by(Professor.name).all()
        assignments = Assignment.query.order_by(Assignment.due_date).all()
        grades = Grades.query.all()
        return render_template('index.html', 
                               assignments=assignments, 
                               professors=professors, 
                               students=students,
                               grades=grades)

@app.route('/delete/student/<int:id>')
def deleteStudent(id):
    student = Student.query.get_or_404(id)

    try:
        db.session.delete(student)
        db.session.commit()
        return redirect('/')
    except:
        return "error"


@app.route("/delete/professor/<int:id>")
def deleteProfessor(id):
    professor = Professor.query.get_or_404(id)

    try:
        db.session.delete(professor)
        db.session.commit()
        return redirect("/")
    except:
        return "error"


@app.route('/update/professor/<int:id>', methods=['GET', 'POST'])
def updateProfessor(id):
    professor = Professor.query.get_or_404(id)

    if request.method == 'POST':
        professor.name = request.form["professorName"]
        professor.email = request.form["professorEmail"]
        professor.department = request.form["professorDepartment"]

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Error updating professor"
    else:
        return render_template('updateProfessor.html', professor=professor)


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
