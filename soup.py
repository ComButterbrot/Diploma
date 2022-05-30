from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

db = SQLAlchemy()
itapp = Flask(__name__)
itapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dtsbasethree.db'
db.init_app(itapp)
itapp.config['SECRET_KEY'] = 'Guess-what-?-You-will-never-guess-!'

class Faculties(db.Model):
    faculty_id = db.Column(db.Integer, primary_key=True)
    faculty_name = db.Column(db.String(128), unique=True, nullable=False)

    departments_data = db.relationship('Departments', backref='faculty', lazy='dynamic')

    def __repr__(self):
        return '<Faculties %r>' %self.faculty_id

class Departments(db.Model):
    department_id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(128), unique=True, nullable=False)
    d_faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.faculty_id'))

    groups_data = db.relationship('Groups', backref='department', lazy='dynamic')

    def __repr__(self):
        return '<Departments %r>' %self.department_id

class Groups(db.Model):
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(128), unique=True, nullable=False)
    g_department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'))

    students_data = db.relationship('Users', backref='group', lazy='dynamic')

    def __repr__(self):
        return '<Groups %r>' %self.group_id

class Users(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(db.String(64), unique=True, nullable=False)
    user_password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    surname = db.Column(db.String(64), nullable=False)
    patronymic = db.Column(db.String(64), nullable=False)
    mail = db.Column(db.String(64), unique=True, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    u_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))

    usercourses_data = db.relationship('UserCourses', backref='user_c', lazy='dynamic')

    userskills_data = db.relationship('UserSkills', backref='userskill_user', lazy='dynamic')

    course_comments_data = db.relationship('CourseComments', backref='course_user_com', lazy='dynamic')

    activity_comments_data = db.relationship('Comments', backref='user_com', lazy='dynamic')

    def get_id(self):
        return (self.user_id)

    def set_password(self, password):
        self.user_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.user_password, password)

    def __repr__(self):
        return f'{self.user_login} | {self.name} {self.surname}'

class Intensives(db.Model):
    m_course_id = db.Column(db.Integer, primary_key=True)
    m_course_name = db.Column(db.String(128), unique=True, nullable=False)
    m_course_description = db.Column(db.String(1024), nullable=False)
    m_course_creator = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    m_comments_data = db.relationship('MainCourseComments', backref='maincourse_comment', lazy='dynamic')

    courses_data = db.relationship('Courses', backref='maincourse_course', lazy='dynamic')

    schedule_data = db.relationship('ScheduledActivities', backref='maincourse_schedule', lazy='dynamic')

    announcements_data = db.relationship('MainCourseAnnouncements', backref='maincourse_announcements', lazy='dynamic')

    def __repr__(self):
        return '<Intensives %r>' %self.m_course_id

class Courses(db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(128), unique=True, nullable=False)
    course_description = db.Column(db.String(1024), nullable=False)
    course_creator = db.Column(db.Integer, nullable=False)
    main_course = db.Column(db.Integer, db.ForeignKey('intensives.m_course_id'))
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    comments_data = db.relationship('CourseComments', backref='course_comment', lazy='dynamic')

    usercourses_data = db.relationship('UserCourses', backref='course', lazy='dynamic')

    activities_data = db.relationship('Activities', backref='course_activity', lazy='dynamic')

    def __repr__(self):
        return '<Courses %r>' %self.course_id

class UserCourses(db.Model):
    uc_id = db.Column(db.Integer, primary_key=True)
    uc_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    uc_course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))
    uc_user_role = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<UserCourses %r>' %self.uc_id

class ScheduledActivities(db.Model):
    s_activity_id = db.Column(db.Integer, primary_key=True)
    s_activity_name = db.Column(db.String(128), nullable=False)
    s_activity_description = db.Column(db.String(1024), nullable=False)
    s_activity_date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))
    m_course_id = db.Column(db.Integer, db.ForeignKey('intensives.m_course_id'))
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    def __repr__(self):
        return '<ScheduledActivities %r>' %self.s_activity_id

class Activities(db.Model):
    activity_id = db.Column(db.Integer, primary_key=True)
    activity_name = db.Column(db.String(128), nullable=False)
    activity_description = db.Column(db.String(1024), nullable=False)
    activity_date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))
    a_course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))
    activity_status = db.Column(db.String(64), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    comments_data = db.relationship('Comments', backref='activity_comment', lazy='dynamic')

    def __repr__(self):
        return '<Activities %r>' %self.activity_id

class Skills(db.Model):
    skill_id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(128), unique=True, nullable=False)
    skill_description = db.Column(db.String(1024), nullable=False)

    userskills_data = db.relationship('UserSkills', backref='userskill_skill', lazy='dynamic')

    def __repr__(self):
        return '<Skills %r>' %self.skill_id

class UserSkills(db.Model):
    us_id = db.Column(db.Integer, primary_key=True)
    us_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    us_skill_id = db.Column(db.Integer, db.ForeignKey('skills.skill_id'))
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    def __repr__(self):
        return '<UserSkills %r>' %self.us_id

class MainCourseAnnouncements(db.Model):
    an_id = db.Column(db.Integer, primary_key=True)
    m_course_id = db.Column(db.Integer, db.ForeignKey('intensives.m_course_id'))
    an_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    an_announcement = db.Column(db.String(1024), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    def __repr__(self):
        return '<MainCourseAnnouncements {}>'.format(self.an_id)

class MainCourseComments(db.Model):
    m_comment_id = db.Column(db.Integer, primary_key=True)
    m_course_id = db.Column(db.Integer, db.ForeignKey('intensives.m_course_id'))
    m_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    m_user_comment = db.Column(db.String(1024), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    def __repr__(self):
        return '<MainCourseComments {}>'.format(self.m_user_comment)

class CourseComments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    c_course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))
    c_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    user_comment = db.Column(db.String(1024), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    def __repr__(self):
        return '<CourseComments {}>'.format(self.user_comment)

class UserCharacteristics(db.Model):
    characteristic_id = db.Column(db.Integer, primary_key=True)
    ch_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    ch_professor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    user_characteristic = db.Column(db.String(1024), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    student = db.relationship('Users', backref='student_ch', foreign_keys=[ch_user_id])
    professor = db.relationship('Users', backref='professor_ch', foreign_keys=[ch_professor_id])

    def __repr__(self):
        return '<UserCharacteristics {}>'.format(self.user_characteristic)

class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    c_activity_id = db.Column(db.String(1024), db.ForeignKey('activities.activity_id'))
    c_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    user_comment = db.Column(db.String(1024), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    def __repr__(self):
        return '<Comments {}>'.format(self.user_comment)

class PrivateMessages(db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    m_sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    m_receiver_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    pmessage = db.Column(db.String(2048), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    sender = db.relationship('Users', backref='sender_m', foreign_keys=[m_sender_id])
    receiver = db.relationship('Users', backref='receiver_m', foreign_keys=[m_receiver_id])

    def __repr__(self):
        return '<PrivateMessages {}>'.format(self.pmessage)

class ConferenceMessages(db.Model):
    cmessage_id = db.Column(db.Integer, primary_key=True)
    cm_sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    cmessage = db.Column(db.String(2048), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")))

    sender = db.relationship('Users', backref='sender_cm', foreign_keys=[cm_sender_id])

    def __repr__(self):
        return '<ConferenceMessages {}>'.format(self.pmessage)