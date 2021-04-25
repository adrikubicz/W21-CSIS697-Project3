from flask import Flask,jsonify,render_template,url_for,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'student.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

    review = db.relationship('Review',backref='student',cascade='all,delete,delete-orphan',lazy=True)

    def __repr__(self):
        return f'<Student(id={self.id}, name={self.name}, email={self.email})>'

    def to_dict(self):
        d={}
        d['id']=self.id
        d['name']=self.name
        d['email']=self.email
    
        review_dict = [b.to_dict() for b in self.review]
        d['reviews'] = review_dict
        return d

    def get_students(self):
        d = {}

        if (len(self.review) == 0):
            d['avg_rating'] = 'N/A'
        
        else:
            d['avg_rating'] = '{:0.2f}'.format(sum([r.get_overall_score() for r in self.review]) / len(self.review))

        d['email'] = self.email
        d['name'] = self.name

        return d

class Review (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    course = db.Column(db.String(100), nullable = False)
    author = db.Column(db.String(100), default = 'Anonymous')
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable = False)
    review = db.Column(db.String(1000), default = 'This student is the worst student I have seen in all my life')
    intelligence = db.Column(db.Integer, db.CheckConstraint('intelligence >= 1 and intelligence <= 5'), default = 3)
    attendance = db.Column(db.Integer, db.CheckConstraint('attendance >= 1 and attendance <= 5'), default = 3)
    participation = db.Column(db.Integer, db.CheckConstraint('participation >= 1 and participation <= 5'), default = 3)
    sarcasm = db.Column(db.Integer, db.CheckConstraint('sarcasm >= 1 and sarcasm <= 5'), default = 3)

    def __repr__(self):
        return f'<Review(id={self.id}, course={self.course}, author={self.author}, student_id={self.student_id}, review={self.review}, intelligence={self.intelligence}, attendance={self.attendance}, participation={self.participation}, sarcasm={self.sarcasm})>'

    def to_dict(self):
        d = {}
        d['id'] = self.id
        d['course'] = self.course
        d['author'] = self.author
        d['student_id'] = self.student_id
        d['review'] = self.review
        d['intelligence'] = self.intelligence
        d['attendance'] = self.attendance
        d['participation'] = self.participation
        d['sarcasm'] = self.sarcasm

    def get_overall_score(self):
        return (self.intelligence + self.attendance + self.participation + self.sarcasm) / 4

def init_db():

    db.create_all()
    db.session.add(Student(name="Harry Potter",email="hpotter@hogwarts.edu"))
    db.session.add(Student(name="Hermione Granger",email="granger@hogwarts.edu"))
    db.session.add(Student(name="Viktor Krum",email="krum@durmstrang.edu"))
    db.session.add(Student(name="Tom Marvolo Riddle",email="iamlordvoldemort@hogwarts.edu"))
    db.session.add(Student(name="Ron Weasley",email="ronny@hogwarts.edu"))
    db.session.add(Student(name="Fleur Delacour",email="fleur@beauxbatons.edu"))
    
    db.session.add(Review(course="Potions-102",student_id=1,review="Mr. Potter is the most arrogant student to have stepped foot into my classroom! ", intelligence=1,attendance=1,sarcasm=5,participation=1))
    db.session.add(Review(course="Charms-401",student_id=1,review="Harry is a brilliant student. He is well on his way to becoming a world famous Auror. ",author='Prof. Flitwick', intelligence=5,attendance=5,sarcasm=5,participation=5))
    db.session.add(Review(course="Herbology-116",student_id=1,review="Potter is one of the smartest students, I have known. He would ace this class, if he didn't sneak out of his dorm every night.  ", intelligence=4,attendance=1,participation=5))
    db.session.add(Review(course="Potions-102",student_id=2,review="Ms. Grainger has the unique distinction of being an insufferable know-it-all ", intelligence=5,attendance=5,participation=1,sarcasm=1))
    db.session.add(Review(course="DADA-400",student_id=2,review="Best student ever!", intelligence=5,attendance=5,participation=5,sarcasm=5))
    db.session.add(Review(course="Quidditch-101",student_id=3,intelligence=1,attendance=5,review="Future World cup Winner!"))
    db.session.add(Review(course="Transfiguration-301",student_id=4,intelligence=5,attendance=5,participation=1,review="A brilliant student. But seems a bit odd. He seems fixated on creating Horcruxes."))
    db.session.add(Review(course="Charms-401",student_id=5,review="Another Weasley! Atleast this one's not as much of a troublemaker like his brothers."))
    db.session.commit()

@app.route('/')
def index():
    return render_template('index.html',bg_file='blog_bg.jpg')

@app.route('/students')
def viewAllStudents():
    res = Student.query.all()
    dlist = [r.get_students() for r in res]
    print(dlist)
    return jsonify(dlist)

@app.route('/students',methods=['POST'])
def createStudent():
    temp = Student(**request.json)
    db.session.add(temp)
    db.session.commit()
    return jsonify(temp.to_dict())

@app.route('/students/<studentName>')
def viewStudent(studentName):
    res = Student.query.filter_by(name = studentName ).first_or_404()
    d = res.to_dict()
    return jsonify(d)

@app.route('/students/<studentName>',methods=['DELETE'])
def deleteStudent(studentName):
    res = Student.query.filter_by(name = studentName ).first_or_404()
    db.session.delete(res)
    db.session.commit()
    return jsonify({'message' : 'Success!'})

@app.route('/blogs')
def viewAllBlogs():
    res = Blog.query.all()
    dlist=[r.to_dict() for r in res]
    print(dlist)
    return jsonify(dlist)

@app.route('/blogs/<int:author>',methods=['POST'])
def createBlog(author):
    temp = Blog(**request.json)
    temp.author = author
    db.session.add(temp)
    db.session.commit()
    return jsonify(temp.to_dict())

@app.route('/blogs/<int:author>')
def viewBlog(author):
    res = Blog.query.filter_by(author=author)
    dlist=[r.to_dict() for r in res]
    print(dlist)
    return jsonify(dlist)

# init_db()

if __name__ == '__main__':
    app.run(debug=True)
