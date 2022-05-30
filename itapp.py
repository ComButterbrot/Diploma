import sys

from flask import render_template, request, redirect, flash
from sqlalchemy import or_, and_

from flask_login import LoginManager, login_user, login_required, current_user
from flask_login import logout_user

from pymystem3 import Mystem
import re
from collections import Counter

from datetime import datetime

from soup import db, itapp, Faculties, Departments, Groups, Users, Intensives, Courses, UserCourses, ScheduledActivities, Activities, Skills, UserSkills, MainCourseAnnouncements, MainCourseComments, CourseComments, UserCharacteristics, Comments, PrivateMessages, ConferenceMessages
from authreg import signup, login
from notification import send_notification

login_manager = LoginManager(itapp)
login_manager.login_view = 'login'
login_manager.init_app(itapp)

def create_app():
    return itapp


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@itapp.route('/user=<int:user_id>', methods=['POST', 'GET'])
@login_required
def user(user_id):
    global current_page
    current_page = "main"
    this_user = Users.query.filter_by(user_id=user_id).first()

    user_group = Groups.query.filter_by(group_id=this_user.u_group_id).first()

    u_courses = Intensives.query.filter_by(m_course_creator=this_user.user_id).group_by(Intensives.m_course_id).all()
    p_courses = db.session.query(Intensives.m_course_id, Intensives.m_course_name, Intensives.m_course_description,
                                 Intensives.m_course_creator, UserCourses.uc_user_role, Courses.course_id,
                                 Courses.main_course).filter(and_(Intensives.m_course_id == Courses.main_course,
                                                                  UserCourses.uc_course_id == Courses.course_id,
                                                                  UserCourses.uc_user_id == this_user.user_id,
                                                                  Intensives.m_course_creator != this_user.user_id)).group_by(Intensives.m_course_id).all()

    u_skills = db.session.query(UserSkills.date, Skills.skill_id, Skills.skill_name, Skills.skill_description).filter(UserSkills.us_user_id == user_id, UserSkills.us_skill_id == Skills.skill_id).all()

    u_characteristics = db.session.query(UserCharacteristics.ch_user_id, UserCharacteristics.ch_professor_id, UserCharacteristics.user_characteristic, UserCharacteristics.date, Users.surname, Users.name, Users.patronymic, Users.u_group_id, Groups.group_id, Groups.group_name).filter(UserCharacteristics.ch_user_id == user_id, UserCharacteristics.ch_professor_id == Users.user_id, Groups.group_id == Users.u_group_id).all()

    if user_group is not None and user_group.group_id != 1 and user_group.group_id != 2:
        user_department = Departments.query.filter_by(department_id=user_group.g_department_id).first()
        user_faculty = Faculties.query.filter_by(faculty_id=user_department.d_faculty_id).first()
    else:
        user_department = Departments.query.first()
        user_faculty = Faculties.query.first()

    if request.method == 'POST':
        ch_user_id = user_id
        ch_professor_id = current_user.user_id
        user_characteristic = request.form['user_characteristic']
        if user_characteristic != "":
            newcharacteristic = UserCharacteristics()
            newcharacteristic.ch_user_id = ch_user_id
            newcharacteristic.ch_professor_id = ch_professor_id
            newcharacteristic.user_characteristic = user_characteristic
            try:
                db.session.add(newcharacteristic)
                db.session.commit()
                return redirect('/user=' + str(user_id))
            except:
                return render_template("userprofile.html", u_courses=u_courses, p_courses=p_courses, u_skills=u_skills, u_characteristics=u_characteristics, current_user=current_user, this_user=this_user, user_group=user_group, user_department=user_department, user_faculty=user_faculty, current_page=current_page)
        else:
            return render_template("userprofile.html", u_courses=u_courses, p_courses=p_courses, u_skills=u_skills, u_characteristics=u_characteristics, current_user=current_user, this_user=this_user, user_group=user_group, user_department=user_department, user_faculty=user_faculty, current_page=current_page)
    return render_template("userprofile.html", u_courses=u_courses, p_courses=p_courses, u_skills=u_skills, u_characteristics=u_characteristics, current_user=current_user, this_user=this_user, user_group=user_group, user_department=user_department, user_faculty=user_faculty, current_page=current_page)


@itapp.route('/user=<int:user_id>-adduserskill', methods=['POST', 'GET'])
@login_required
def adduserskill(user_id):
    global current_page
    current_page = "notmain"
    all_skills = Skills.query.order_by(Skills.skill_id).all()

    if request.method == 'POST':
        us_user_id = user_id
        us_skill_id = request.form['user_skill']

        currentuserskill = UserSkills.query.filter_by(us_user_id=us_user_id).filter_by(us_skill_id=us_skill_id).first()

        if currentuserskill is not None:
            flash('Этот пользователь уже освоил данную компетенцию.')
            return redirect('/user=' + str(user_id) +'-adduserskill')
        else:
            new_us = UserSkills()
            new_us.us_user_id = us_user_id
            new_us.us_skill_id = us_skill_id
            try:
                db.session.add(new_us)
                db.session.commit()
                return redirect('/user=' + str(user_id))
            except:
                return render_template("adduserskill.html", all_skills=all_skills, current_user=current_user, current_page=current_page)
    else:
        return render_template("adduserskill.html", all_skills=all_skills, current_user=current_user, current_page=current_page)


@itapp.route('/secretadmin-settings')
@login_required
def settings():
    global current_page
    current_page = "main"

    v_users = Users.query.filter_by(u_group_id=3).order_by(Users.date).all()

    all_faculties = Faculties.query.all()

    all_departments = Departments.query.all()

    all_skills = Skills.query.all()

    return render_template("settings.html", v_users=v_users, all_faculties=all_faculties, all_departments=all_departments, all_skills=all_skills, current_user=current_user, current_page=current_page)


@itapp.route('/faculties')
@login_required
def faculties():
    global current_page
    current_page = "notmain"

    all_faculties = Faculties.query.all()

    all_departments = Departments.query.all()

    return render_template("facultiespage.html", current_user=current_user, current_page=current_page, all_faculties=all_faculties, all_departments=all_departments)


@itapp.route('/faculty=<int:faculty_id>-department=<int:department_id>')
@login_required
def department(faculty_id, department_id):
    global current_page
    current_page = "main"

    current_department = Departments.query.filter_by(department_id=department_id).first()

    valid_groups = Groups.query.filter_by(g_department_id=department_id).order_by(Groups.group_name.desc()).all()

    return render_template("departmentpage.html", faculty_id=faculty_id, current_department=current_department, valid_groups=valid_groups, current_user=current_user, current_page=current_page)


@itapp.route('/faculty=<int:faculty_id>-department=<int:department_id>-group=<int:group_id>')
@login_required
def group(faculty_id, department_id, group_id):
    global current_page
    current_page = "main"

    current_group = Groups.query.filter_by(group_id=group_id).first()

    valid_users = Users.query.filter_by(u_group_id=current_group.group_id).order_by(Users.surname).all()

    return render_template("grouppage.html", faculty_id=faculty_id, current_group=current_group, valid_users=valid_users, current_user=current_user, current_page=current_page)


@itapp.route('/addmaincourse', methods=['POST', 'GET'])
@login_required
def addmaincourse():
    global current_page
    current_page = "notmain"
    allcourses = Intensives.query.order_by(Intensives.m_course_name).all()
    if request.method == 'POST':
        m_course_name = request.form['course_name']
        m_course_description = request.form['course_description']
        m_course_creator = current_user.user_id

        currentcourse = Intensives.query.filter_by(m_course_name=m_course_name).first()

        if currentcourse is not None:
            flash('This course already exists!')
            return redirect('/addmaincourse')
        else:
            newmaincourse = Intensives()
            newmaincourse.m_course_name = m_course_name
            newmaincourse.m_course_description = m_course_description
            newmaincourse.m_course_creator = m_course_creator
            try:
                db.session.add(newmaincourse)
                db.session.commit()
                return redirect('/maincourse=' + str(
                    Intensives.query.filter_by(m_course_creator=m_course_creator, m_course_name=m_course_name).order_by(
                        Intensives.date).first().m_course_id))
            except:
                return render_template("newmaincourse.html", current_user=current_user, current_page=current_page)
    else:
        return render_template("newmaincourse.html", current_user=current_user, allcourses=allcourses, current_page=current_page)


@itapp.route('/maincourse=<int:m_course_id>-addcourse', methods=['POST', 'GET'])
@login_required
def addcourse(m_course_id):
    global current_page
    current_page = "notmain"
    allcourses = Courses.query.order_by(Courses.course_name).all()
    m_scheduledactivities = ScheduledActivities.query.filter_by(m_course_id=m_course_id).all()
    if request.method == 'POST':
        course_name = request.form['course_name']
        course_description = request.form['course_description']
        course_creator = current_user.user_id
        main_course = m_course_id

        currentcourse = Courses.query.filter_by(course_name=course_name).first()

        if currentcourse is not None:
            flash('This course already exists!')
            return redirect('/addcourse')
        else:
            newcourse = Courses()
            newcourse.course_name = course_name
            newcourse.course_description = course_description
            newcourse.course_creator = course_creator
            newcourse.main_course = main_course
            try:
                db.session.add(newcourse)
                db.session.commit()
                c_course = Courses.query.filter_by(course_name=course_name, main_course=main_course).first()
                for ms_activity in m_scheduledactivities:
                    newactivity = Activities()
                    newactivity.activity_name = ms_activity.s_activity_name
                    newactivity.activity_description = ms_activity.s_activity_description
                    newactivity.a_course_id = c_course.course_id
                    newactivity.activity_status = "global"
                    db.session.add(newactivity)
                    db.session.commit()
            except:
                return render_template("newcourse.html", current_user=current_user, current_page=current_page)

            try:
                new_uc = UserCourses()
                new_uc.uc_user_id = course_creator
                new_uc.uc_course_id = Courses.query.filter_by(course_creator=course_creator, course_name=course_name).order_by(Courses.date).first().course_id
                new_uc.uc_user_role = 'Старший тьютор'
                db.session.add(new_uc)
                db.session.commit()
                return redirect('/maincourse=' + str(m_course_id) + '-course=' + str(Courses.query.filter_by(course_creator=course_creator, course_name=course_name).order_by(Courses.date).first().course_id))
            except:
                return render_template("newcourse.html", current_user=current_user, current_page=current_page)
    else:
        return render_template("newcourse.html", current_user=current_user, allcourses=allcourses, current_page=current_page)


@itapp.route('/maincourse=<int:m_course_id>', methods=['POST', 'GET'])
@login_required
def maincourse(m_course_id):
    global current_page
    current_page = "notmain"
    current_course = Intensives.query.filter_by(m_course_id=m_course_id).first()
    m_courses = Courses.query.filter_by(main_course=m_course_id).order_by(Courses.course_name).all()
    m_scheduledactivities = ScheduledActivities.query.filter_by(m_course_id=m_course_id).order_by(ScheduledActivities.s_activity_date).all()
    all_users = Users.query.all()

    c_creator = db.session.query(Intensives.m_course_id, Intensives.m_course_creator, Groups.group_id,
                                 Groups.group_name, Users.user_id, Users.surname, Users.name, Users.patronymic,
                                 Users.u_group_id).filter(m_course_id == Intensives.m_course_id,
                                                          Users.user_id == Intensives.m_course_creator).first()
    c_users = db.session.query(Courses.course_name, Courses.main_course, Groups.group_id, Groups.group_name,
                               Users.user_id, Users.surname, Users.name, Users.patronymic, Users.mail, Users.u_group_id,
                               UserCourses.uc_user_role).filter(m_course_id == Courses.main_course,
                                                                UserCourses.uc_course_id == Courses.course_id,
                                                                UserCourses.uc_user_id == Users.user_id,
                                                                Groups.group_id == Users.u_group_id).group_by(Users.user_id).all()
    c_leaders = db.session.query(Courses.course_name, Courses.main_course, Groups.group_id, Groups.group_name,
                                 Users.user_id, Users.surname, Users.name, Users.patronymic, Users.u_group_id,
                                 UserCourses.uc_user_role).filter(m_course_id == Courses.main_course,
                                                                  UserCourses.uc_course_id == Courses.course_id,
                                                                  UserCourses.uc_user_role == "Тьютор",
                                                                  Users.user_id == UserCourses.uc_user_id,
                                                                  Groups.group_id == Users.u_group_id).group_by(Users.user_id).all()
    u_comments = db.session.query(Courses.course_name, Courses.main_course, Groups.group_id, Groups.group_name,
                                  Users.user_id, Users.surname, Users.name, Users.patronymic, Users.u_group_id,
                                  MainCourseComments.m_user_comment, MainCourseComments.date,
                                  UserCourses.uc_user_role).filter(m_course_id == Courses.main_course,
                                                                   UserCourses.uc_course_id == Courses.course_id,
                                                                   UserCourses.uc_user_id == Users.user_id,
                                                                   MainCourseComments.m_user_id == Users.user_id,
                                                                   MainCourseComments.m_course_id == m_course_id,
                                                                   Groups.group_id == Users.u_group_id).group_by(MainCourseComments.m_comment_id).all()
    c_announcements = db.session.query(Groups.group_id, Groups.group_name,
                                       Users.user_id, Users.surname, Users.name, Users.patronymic, Users.u_group_id,
                                       MainCourseAnnouncements.an_id, MainCourseAnnouncements.an_announcement,
                                       MainCourseAnnouncements.an_user_id, MainCourseAnnouncements.m_course_id,
                                       MainCourseAnnouncements.date).filter(m_course_id == MainCourseAnnouncements.m_course_id,
                                                                            MainCourseAnnouncements.an_user_id == Users.user_id,
                                                                            Groups.group_id == Users.u_group_id).group_by(MainCourseAnnouncements.an_id).all()

    logged_user = db.session.query(Courses.course_name, Courses.main_course, UserCourses.uc_user_role,
                                   Users.user_id, Users.surname, Users.name, Users.patronymic,
                                   Users.u_group_id).filter(Users.user_login == current_user.user_login,
                                                            Courses.main_course == m_course_id,
                                                            UserCourses.uc_user_id == Users.user_id,
                                                            UserCourses.uc_course_id == Courses.course_id).first()

    if request.method == 'POST':
        m_course_id = m_course_id

        m_user_id = current_user.user_id
        m_user_comment = request.form.get('user_comment', False)

        an_user_id = current_user.user_id
        an_announcement = request.form.get('user_announcement', False)

        if m_user_comment != "" and m_user_comment is not False and an_announcement != "" and an_announcement is not False:
            newcomment = MainCourseComments()
            newcomment.m_course_id = m_course_id
            newcomment.m_user_id = m_user_id
            newcomment.m_user_comment = m_user_comment
            newannouncement = MainCourseAnnouncements()
            newannouncement.m_course_id = m_course_id
            newannouncement.an_user_id = an_user_id
            newannouncement.an_announcement = an_announcement
            try:
                db.session.add(newcomment)
                db.session.commit()
                db.session.add(newannouncement)
                db.session.commit()

                an_author = Users.query.filter_by(user_id=an_user_id).first()
                new_announcement = MainCourseAnnouncements.query.order_by(MainCourseAnnouncements.date.desc()).first()
                subject = "ЭСТ КГУ: Новое объявление в курсе \"" + current_course.m_course_name + "\"."
                for c_user in c_users:
                    recipient = c_user.mail
                    body_text = "Здравствуйте, " + c_user.name + " " + c_user.patronymic + "!\nВ курсе \"" + current_course.m_course_name + "\" было размещено новое объявление:\n\n" + an_author.surname + " " + an_author.name + " " + an_author.patronymic + " | " + new_announcement.date.strftime('%d.%m.%Y') + "\n" + an_announcement
                    send_notification(subject, recipient, body_text)
                return redirect('/maincourse=' + str(m_course_id))
            except:
                return render_template("maincoursepage.html", all_users=all_users, m_courses=m_courses, m_scheduledactivities=m_scheduledactivities, c_creator=c_creator, c_users=c_users, c_leaders=c_leaders, current_user=current_user, logged_user=logged_user, current_course=current_course, u_comments=u_comments, current_page=current_page, c_announcements=c_announcements)
        elif m_user_comment != "" and (an_announcement == "" or an_announcement is False):
            newcomment = MainCourseComments()
            newcomment.m_course_id = m_course_id
            newcomment.m_user_id = m_user_id
            newcomment.m_user_comment = m_user_comment
            try:
                db.session.add(newcomment)
                db.session.commit()
                return redirect('/maincourse=' + str(m_course_id))
            except:
                return render_template("maincoursepage.html", all_users=all_users, m_courses=m_courses, m_scheduledactivities=m_scheduledactivities, c_creator=c_creator, c_users=c_users, c_leaders=c_leaders, current_user=current_user, logged_user=logged_user, current_course=current_course, u_comments=u_comments, current_page=current_page, c_announcements=c_announcements)
        elif (m_user_comment == "" or m_user_comment is False) and an_announcement != "":
            newannouncement = MainCourseAnnouncements()
            newannouncement.m_course_id = m_course_id
            newannouncement.an_user_id = an_user_id
            newannouncement.an_announcement = an_announcement
            try:
                db.session.add(newannouncement)
                db.session.commit()

                an_author = Users.query.filter_by(user_id=an_user_id).first()
                new_announcement = MainCourseAnnouncements.query.order_by(MainCourseAnnouncements.date.desc()).first()
                subject = "ЭСТ КГУ: Новое объявление в курсе \"" + current_course.m_course_name + "\"."
                for c_user in c_users:
                    recipient = c_user.mail
                    body_text = "Здравствуйте, " + c_user.name + " " + c_user.patronymic + "!\nВ курсе \"" + current_course.m_course_name + "\" было размещено новое объявление.\n\n" + an_author.surname + " " + an_author.name + " " + an_author.patronymic + " | " + new_announcement.date.strftime('%d.%m.%Y') + "\n" + an_announcement
                    send_notification(subject, recipient, body_text)
                return redirect('/maincourse=' + str(m_course_id))
            except:
                return render_template("maincoursepage.html", all_users=all_users, m_courses=m_courses, m_scheduledactivities=m_scheduledactivities, c_creator=c_creator, c_users=c_users, c_leaders=c_leaders, current_user=current_user, logged_user=logged_user, current_course=current_course, u_comments=u_comments, current_page=current_page, c_announcements=c_announcements)
        else:
            return render_template("maincoursepage.html", all_users=all_users, m_courses=m_courses, m_scheduledactivities=m_scheduledactivities, c_creator=c_creator, c_users=c_users, c_leaders=c_leaders, current_user=current_user, logged_user=logged_user, current_course=current_course, u_comments=u_comments, current_page=current_page, c_announcements=c_announcements)

    else:
        return render_template("maincoursepage.html", all_users=all_users, m_courses=m_courses, m_scheduledactivities=m_scheduledactivities, c_creator=c_creator, c_users=c_users, c_leaders=c_leaders, current_user=current_user, logged_user=logged_user, current_course=current_course, u_comments=u_comments, current_page=current_page, c_announcements=c_announcements)


@itapp.route('/maincourse=<int:m_course_id>-course=<int:course_id>', methods=['POST', 'GET'])
@login_required
def course(m_course_id, course_id):
    global current_page
    current_page = "notmain"
    current_course = Courses.query.filter_by(course_id=course_id).first()
    current_maincourse = Intensives.query.filter_by(m_course_id=current_course.main_course).first()
    c_activities = Activities.query.filter_by(a_course_id=course_id, activity_status="local").order_by(Activities.activity_date).all()
    m_activities = Activities.query.filter_by(a_course_id=course_id, activity_status="global").order_by(Activities.activity_date).all()
    all_users = Users.query.all()

    logged_user = "NaN"
    c_users = db.session.query(Groups.group_id, Groups.group_name, Users.user_id, Users.surname, Users.name, Users.patronymic, Users.u_group_id, UserCourses.uc_user_role).filter(Users.user_id == UserCourses.uc_user_id, UserCourses.uc_course_id == course_id, Groups.group_id == Users.u_group_id).all()
    u_comments = db.session.query(Groups.group_id, Groups.group_name, Users.user_id, Users.surname, Users.name, Users.patronymic, Users.u_group_id, CourseComments.user_comment, CourseComments.date, UserCourses.uc_user_role).filter(Users.user_id == UserCourses.uc_user_id, UserCourses.uc_course_id == course_id, Users.user_id == CourseComments.c_user_id, CourseComments.c_course_id == course_id, Groups.group_id == Users.u_group_id).all()

    common_words = []
    total_words_count = wordscount(course_id)
    if total_words_count != 0:
        c_words = textparser(course_id)
        for c_word in c_words:
            c_word_line = ''
            for c_data in c_word:
                c_word_line = c_word_line + str(c_data) + ' - '
            c_word_line += '|'
            c_word_line = (c_word_line.replace(' - |', ''))
            common_words.append(c_word_line)

    logged_user = db.session.query(UserCourses.uc_user_role, Users.user_id, Users.surname, Users.name, Users.patronymic,
                                   Users.u_group_id).filter(Users.user_login == current_user.user_login,
                                                            UserCourses.uc_user_id == Users.user_id,
                                                            UserCourses.uc_course_id == course_id).first()

    if request.method == 'POST':
        c_course_id = course_id
        c_user_id = current_user.user_id
        user_comment = request.form['user_comment']
        if user_comment != "":
            newcomment = CourseComments()
            newcomment.c_course_id = c_course_id
            newcomment.c_user_id = c_user_id
            newcomment.user_comment = user_comment
            try:
                db.session.add(newcomment)
                db.session.commit()
                return redirect('/maincourse=' + str(m_course_id) + '-course=' + str(course_id))
            except:
                return render_template("coursepage.html", all_users=all_users, c_users=c_users, current_maincourse=current_maincourse, current_user=current_user, logged_user=logged_user, current_course=current_course, m_activities=m_activities, c_activities=c_activities, u_comments=u_comments, current_page=current_page, common_words=common_words, total_words_count=total_words_count)
        else:
            return render_template("coursepage.html", all_users=all_users, c_users=c_users,
                                   current_maincourse=current_maincourse, current_user=current_user,
                                   logged_user=logged_user, current_course=current_course, m_activities=m_activities,
                                   c_activities=c_activities, u_comments=u_comments,
                                   current_page=current_page,
                                   common_words=common_words, total_words_count=total_words_count)
    else:
        return render_template("coursepage.html", all_users=all_users, c_users=c_users, current_maincourse=current_maincourse, current_user=current_user, logged_user=logged_user, current_course=current_course, m_activities=m_activities, c_activities=c_activities, u_comments=u_comments, current_page=current_page, common_words=common_words, total_words_count=total_words_count)


@itapp.route('/maincourse=<int:m_course_id>-course=<int:course_id>-addparticipant', methods=['POST', 'GET'])
@login_required
def addparticipant(m_course_id, course_id):
    global current_page
    current_page = "notmain"
    current_course = Courses.query.filter_by(course_id=course_id).first()
    cc_name = current_course.course_name
    current_maincourse = Intensives.query.filter_by(m_course_id=current_course.main_course).first()
    cmc_name = current_maincourse.m_course_name
    c_activities = Activities.query.filter_by(a_course_id=course_id).order_by(Activities.date.desc()).all()
    all_users = db.session.query(Courses.course_id, Courses.main_course, Groups.group_id, Groups.group_name,
                                 Users.user_id, Users.surname, Users.name, Users.patronymic, Users.u_group_id,
                                 UserCourses.uc_user_role).filter(and_(m_course_id == Courses.main_course,
                                                                       UserCourses.uc_course_id == Courses.course_id,
                                                                       Users.user_id != UserCourses.uc_user_id,
                                                                       Groups.group_id == Users.u_group_id)).group_by(Users.user_id).all()
    c_users = UserCourses.query.filter_by(uc_course_id=course_id).all()


    logged_user = db.session.query(UserCourses.uc_user_role, Users.user_id, Users.surname, Users.name,
                                   Users.patronymic, Users.u_group_id).filter(
        UserCourses.uc_user_id == current_user.user_id, UserCourses.uc_course_id == course_id).first()

    if request.method == 'POST':
        uc_course_id = course_id
        uc_user_id = request.form['user_participant']
        uc_user_role = request.form['user_role']

        currentparticipant = UserCourses.query.filter_by(uc_course_id=uc_course_id).filter_by(uc_user_id=uc_user_id).first()

        if currentparticipant is not None:
            flash('Этот пользователь уже добавлен в команду.')
            return redirect('/maincourse=' + str(m_course_id) + '-course=' + str(course_id) +'-addparticipant')
        else:
            new_uc = UserCourses()
            new_uc.uc_user_id = uc_user_id
            new_uc.uc_course_id = uc_course_id
            new_uc.uc_user_role = uc_user_role
            try:
                db.session.add(new_uc)
                db.session.commit()

                new_participant = Users.query.filter_by(user_id=uc_user_id).first()

                subject = "ЭСТ КГУ: Регистрация в проекте \"" + cc_name + "\"."
                recipient = new_participant.mail
                body_text = "Здравствуйте, " + new_participant.name + " " + new_participant.patronymic + "!\nВы были добавлены в проект \"" + cc_name + "\" курса \"" + cmc_name + "\".\nТекущая роль - \"" + uc_user_role + "\"."
                send_notification(subject, recipient, body_text)
                return redirect('/maincourse=' + str(m_course_id) + '-course=' + str(course_id))
            except:
                print(sys.exc_info()[0])
                return render_template("newparticipant.html", all_users=all_users, c_users=c_users, current_user=current_user, logged_user=logged_user, current_course=current_course, c_activities=c_activities, current_page=current_page)
    else:
        return render_template("newparticipant.html", all_users=all_users, c_users=c_users, current_user=current_user, logged_user=logged_user, current_course=current_course, c_activities=c_activities, current_page=current_page)


@itapp.route('/maincourse=<int:m_course_id>-course=<int:course_id>-user=<int:user_id>/removeparticipant')
@login_required
def removeparticipant(m_course_id, course_id, user_id):
    global current_page
    current_page = "notmain"
    currentuser = UserCourses.query.filter_by(uc_user_id=user_id, uc_course_id=course_id).first()
    try:
        db.session.delete(currentuser)
        db.session.commit()
        return redirect('/maincourse=' + str(m_course_id) + '-course=' + str(course_id))
    except:
        return redirect('/maincourse=' + str(m_course_id) + '-course=' + str(course_id))


@itapp.route('/maincourse=<int:m_course_id>-course=<int:course_id>-newactivity', methods=['POST', 'GET'])
@login_required
def createactivity(m_course_id, course_id):
    global current_page
    current_page = "notmain"
    current_course = Courses.query.filter_by(course_id=course_id).first()
    сurrent_maincourse = Intensives.query.filter_by(m_course_id=m_course_id).first()
    c_activities = Activities.query.filter_by(a_course_id=course_id).order_by(Activities.date.desc()).all()
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

    if request.method == 'POST':
        a_course_id = course_id

        activity_name = request.form['activity_name']
        activity_description = request.form['activity_description']
        activity_date = datetime.strptime(request.form['activity_date'] + " 00:00:00", '%Y-%m-%d %H:%M:%S')

        newactivity = Activities()
        newactivity.activity_name = activity_name
        newactivity.activity_description = activity_description
        newactivity.activity_date = activity_date
        newactivity.a_course_id = a_course_id
        newactivity.activity_status = "local"
        try:
            db.session.add(newactivity)
            db.session.commit()
            c_users = db.session.query(Groups.group_id, Groups.group_name, Users.user_id, Users.surname, Users.name,
                                       Users.patronymic, Users.mail, Users.u_group_id, UserCourses.uc_user_role).filter(
                Users.user_id == UserCourses.uc_user_id, UserCourses.uc_course_id == course_id,
                Groups.group_id == Users.u_group_id).all()

            subject = "ЭСТ КГУ: Новое внутреннее мероприятие в проекте \"" + current_course.course_name + "\"."
            for c_user in c_users:
                recipient = c_user.mail
                body_text = "Здравствуйте, " + c_user.name + " " + c_user.patronymic + "!\nВ проекте \"" + current_course.course_name + "\" курса \"" + сurrent_maincourse.m_course_name + "\" было создано внутреннее мероприятие \"" + activity_name + "\"\nДата проведения мероприятия - " + activity_date.strftime('%d.%m.%Y') + "."
                send_notification(subject, recipient, body_text)
            return redirect('/maincourse=' + str(m_course_id) + '-course=' + str(course_id) + '-activity=' + str(Activities.query.filter_by(a_course_id=course_id).order_by(Activities.date.desc()).first().activity_id))
        except:
            return render_template("newactivity.html", current_user=current_user, current_course=current_course, c_activities=c_activities, current_page=current_page, current_day=current_day, current_month=current_month, current_year=current_year)
    else:
        return render_template("newactivity.html", current_user=current_user, current_course=current_course, c_activities=c_activities, current_page=current_page, current_day=current_day, current_month=current_month, current_year=current_year)


@itapp.route('/maincourse=<int:m_course_id>-newscheduledactivity', methods=['POST', 'GET'])
@login_required
def createscheduledactivity(m_course_id):
    global current_page
    current_page = "notmain"
    current_maincourse = Intensives.query.filter_by(m_course_id=m_course_id).first()
    s_activities = ScheduledActivities.query.filter_by(m_course_id=m_course_id).order_by(ScheduledActivities.date.desc()).all()
    l_courses = Courses.query.filter_by(main_course=m_course_id).all()
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

    if request.method == 'POST':
        m_course_id = m_course_id

        s_activity_name = request.form['activity_name']
        s_activity_description = request.form['activity_description']
        s_activity_date = datetime.strptime(request.form['activity_date'] + " 00:00:00", '%Y-%m-%d %H:%M:%S')

        newascheduledctivity = ScheduledActivities()
        newascheduledctivity.s_activity_name = s_activity_name
        newascheduledctivity.s_activity_description = s_activity_description
        newascheduledctivity.s_activity_date = s_activity_date
        newascheduledctivity.m_course_id = m_course_id
        try:
            db.session.add(newascheduledctivity)
            db.session.commit()
            for l_course in l_courses:
                newactivity = Activities()
                newactivity.activity_name = s_activity_name
                newactivity.activity_description = s_activity_description
                newactivity.activity_date = s_activity_date
                newactivity.a_course_id = l_course.course_id
                newactivity.activity_status = "global"
                db.session.add(newactivity)
                db.session.commit()

            c_users = db.session.query(Courses.course_name, Courses.main_course, Groups.group_id, Groups.group_name,
                                       Users.user_id, Users.surname, Users.name, Users.mail, Users.patronymic, Users.u_group_id,
                                       UserCourses.uc_user_role).filter(m_course_id == Courses.main_course,
                                                                        UserCourses.uc_course_id == Courses.course_id,
                                                                        UserCourses.uc_user_id == Users.user_id,
                                                                        Groups.group_id == Users.u_group_id).group_by(
                Users.user_id).all()

            subject = "ЭСТ КГУ: Новое общее мероприятие в курсе \"" + current_maincourse.m_course_name + "\""
            for c_user in c_users:
                recipient = c_user.mail
                body_text = "Здравствуйте, " + c_user.name + " " + c_user.patronymic + "!\nВ курсе \"" + current_maincourse.m_course_name + "\" было создано общее мероприятие \"" + s_activity_name + "\". "
                send_notification(subject, recipient, body_text)

            return redirect('/maincourse=' + str(m_course_id))
        except:
            return render_template("newscheduledactivity.html", current_user=current_user, current_maincourse=current_maincourse, s_activities=s_activities, current_page=current_page, current_day=current_day, current_month=current_month, current_year=current_year)
    else:
        return render_template("newscheduledactivity.html", current_user=current_user, current_maincourse=current_maincourse, s_activities=s_activities, current_page=current_page, current_day=current_day, current_month=current_month, current_year=current_year)


@itapp.route('/maincourse=<int:m_course_id>-course=<int:course_id>-activity=<int:activity_id>', methods=['POST', 'GET'])
@login_required
def activity(m_course_id, course_id, activity_id):
    global current_page
    current_page = "notmain"
    current_course = Courses.query.filter_by(course_id=course_id).first()
    current_activity = Activities.query.filter_by(activity_id=activity_id).first()

    c_users = db.session.query(Groups.group_id, Groups.group_name, Users.user_id, Users.surname, Users.name, Users.patronymic, Users.u_group_id, UserCourses.uc_user_role).filter(Users.user_id == UserCourses.uc_user_id, UserCourses.uc_course_id == course_id, Groups.group_id == Users.u_group_id).all()

    u_comments = db.session.query(Groups.group_id, Groups.group_name, Users.user_id, Users.surname, Users.name, Users.patronymic, Users.u_group_id, Comments.user_comment, Comments.date, UserCourses.uc_user_role).filter(Users.user_id == UserCourses.uc_user_id, UserCourses.uc_course_id == course_id, Users.user_id == Comments.c_user_id, Comments.c_activity_id == activity_id, Groups.group_id == Users.u_group_id).all()

    if request.method == 'POST':
        c_activity_id = activity_id
        c_user_id = current_user.user_id
        user_comment = request.form['user_comment']
        if user_comment != "":
            newcomment = Comments()
            newcomment.c_activity_id = c_activity_id
            newcomment.c_user_id = c_user_id
            newcomment.user_comment = user_comment
            try:
                db.session.add(newcomment)
                db.session.commit()
                return redirect('/maincourse=' + str(m_course_id) + '-course=' + str(course_id) + '-activity=' + str(activity_id))
            except:
                return render_template("activitypage.html", c_users=c_users, current_user=current_user, current_course=current_course, current_activity=current_activity, u_comments=u_comments, current_page=current_page)
        else:
            return render_template("activitypage.html", c_users=c_users, current_user=current_user, current_course=current_course, current_activity=current_activity, u_comments=u_comments, current_page=current_page)
    else:
        return render_template("activitypage.html", c_users=c_users, current_user=current_user, current_course=current_course, current_activity=current_activity, u_comments=u_comments, current_page=current_page)


@itapp.route('/messenger')
@login_required
def messenger():
    global current_page
    current_page = "notmain"

    user_receivers = db.session.query(Groups.group_id, Groups.group_name, Users.user_id, Users.surname, Users.name, Users.patronymic, Users.u_group_id, PrivateMessages.pmessage, PrivateMessages.date).filter(and_(Groups.group_id == Users.u_group_id, or_(and_(Users.user_id != current_user.user_id, Users.user_id == PrivateMessages.m_sender_id, current_user.user_id == PrivateMessages.m_receiver_id), and_(Users.user_id != current_user.user_id, Users.user_id == PrivateMessages.m_receiver_id, current_user.user_id == PrivateMessages.m_sender_id)))).distinct(PrivateMessages.m_receiver_id).distinct(PrivateMessages.m_sender_id).group_by(Users.user_id).all()

    return render_template("messengerpage.html", current_user=current_user, current_page=current_page, user_receivers=user_receivers)


@itapp.route('/user=<int:user_id>-dialogue', methods=['POST', 'GET'])
@login_required
def dialogue(user_id):
    global current_page
    current_page = "notmain"

    this_user = db.session.query(Groups.group_id, Groups.group_name, Users.user_id, Users.surname, Users.name, Users.patronymic,
                                 Users.u_group_id).filter(Users.user_id == user_id, Groups.group_id == Users.u_group_id).first()
    user_messages = db.session.query(Groups.group_id, Groups.group_name, Users.user_id, Users.surname, Users.name, Users.patronymic, Users.u_group_id, PrivateMessages.m_sender_id, PrivateMessages.pmessage, PrivateMessages.date).filter(and_(Groups.group_id == Users.u_group_id, Users.user_id == PrivateMessages.m_sender_id, or_(and_(current_user.user_id == PrivateMessages.m_sender_id, this_user.user_id == PrivateMessages.m_receiver_id, current_user.user_id != PrivateMessages.m_receiver_id, this_user.user_id != PrivateMessages.m_sender_id), and_(current_user.user_id == PrivateMessages.m_receiver_id, this_user.user_id == PrivateMessages.m_sender_id, current_user.user_id != PrivateMessages.m_sender_id, this_user.user_id != PrivateMessages.m_receiver_id)))).distinct(PrivateMessages.m_receiver_id).distinct(PrivateMessages.m_sender_id).all()

    if request.method == 'POST':
        m_sender_id = current_user.user_id
        m_receiver_id = this_user.user_id
        pmessage = request.form['user_message']
        if pmessage != "":
            newmessage = PrivateMessages()
            newmessage.m_sender_id = m_sender_id
            newmessage.m_receiver_id = m_receiver_id
            newmessage.pmessage = pmessage
            try:
                db.session.add(newmessage)
                db.session.commit()
                return redirect('/user=' + str(user_id) + '-dialogue')
            except:
                return render_template("dialoguepage.html", this_user=this_user, current_user=current_user, current_page=current_page)
        else:
            return render_template("dialoguepage.html", this_user=this_user, current_user=current_user,
                                   current_page=current_page)
    return render_template("dialoguepage.html", this_user=this_user, current_user=current_user, user_messages=user_messages, current_page=current_page)


@itapp.route('/conference', methods=['POST', 'GET'])
@login_required
def conference():
    global current_page
    current_page = "notmain"

    tutor_messages = db.session.query(Groups.group_id, Groups.group_name, Users.user_id, Users.surname, Users.name, Users.patronymic, Users.u_group_id, ConferenceMessages.cmessage, ConferenceMessages.date).filter(or_(Users.u_group_id == 1, Users.u_group_id == 2), ConferenceMessages.cm_sender_id == Users.user_id, Groups.group_id == Users.u_group_id).all()

    if request.method == 'POST':
        cmessage = request.form['user_message']
        if cmessage != "":
            newmessage = ConferenceMessages()
            newmessage.cm_sender_id = current_user.user_id
            newmessage.cmessage = cmessage
            try:
                db.session.add(newmessage)
                db.session.commit()
                return redirect('/conference')
            except:
                return render_template("conferencepage.html", current_user=current_user, tutor_messages=tutor_messages, current_page=current_page)
        else:
            return render_template("conferencepage.html", current_user=current_user, tutor_messages=tutor_messages, current_page=current_page)
    return render_template("conferencepage.html", current_user=current_user, tutor_messages=tutor_messages, current_page=current_page)


@itapp.route('/secretadmin-addskill', methods=['POST', 'GET'])
@login_required
def addskill():
    global current_page
    current_page = "notmain"
    if request.method == 'POST':
        skill_name = request.form['skill_name']
        skill_description = request.form['skill_description']

        currentskill = Skills.query.filter_by(skill_name=skill_name).first()

        if currentskill is not None:
            flash('This skill already exists!')
            return redirect('/secretadmin-addskill')
        else:
            newskill = Skills()
            newskill.skill_name = skill_name
            newskill.skill_description = skill_description
            try:
                db.session.add(newskill)
                db.session.commit()
                return redirect('/skills')
            except:
                return render_template("newskill.html", current_user=current_user, current_page=current_page)
    else:
        return render_template("newskill.html", current_user=current_user, current_page=current_page)


@itapp.route('/skills', methods=['POST', 'GET'])
@login_required
def skills():
    global current_page
    current_page = "main"
    all_skills = Skills.query.order_by(Skills.skill_id).all()

    u_courses = db.session.query(UserCourses.uc_user_role, Courses.course_id, Courses.course_name, Courses.course_description).filter(UserCourses.uc_user_id == current_user.user_id, UserCourses.uc_course_id == Courses.course_id).all()

    if request.method == 'POST':
        search_course = request.form['search_course'] + "%"
        search_string = search_course.replace(' ', '').replace(',', '').replace('.', '').replace(':', '').replace(';', '').replace('?', '').replace('!', '').replace('-', '')

        return redirect('/search=' + search_string)
    else:
        return render_template("skillspage.html", u_courses=u_courses, all_skills=all_skills, current_user=current_user, current_page=current_page)


@itapp.route('/secretadmin-v_user=<int:user_id>/decline')
@login_required
def declineuser(user_id):
    global current_page
    current_page = "notmain"
    currentuser = Users.query.get_or_404(user_id)
    try:
        db.session.delete(currentuser)
        db.session.commit()
        return redirect('/secretadmin-settings')
    except:
        return render_template("settings.html", current_page=current_page)


@itapp.route('/secretadmin-v_user=<int:user_id>/verify')
@login_required
def verifyuser(user_id):
    global current_page
    current_page = "notmain"
    verifieduser = Users.query.get_or_404(user_id)

    newuser = Users()
    newuser.user_login = verifieduser.user_login
    newuser.user_password = verifieduser.user_password
    newuser.name = verifieduser.name
    newuser.surname = verifieduser.surname
    newuser.patronymic = verifieduser.patronymic
    newuser.mail = verifieduser.mail
    newuser.u_group_id = 2
    try:
        db.session.delete(verifieduser)
        db.session.commit()
        db.session.add(newuser)
        db.session.commit()
        return redirect('/secretadmin-settings')
    except:
        return render_template("settings.html", current_page=current_page)


def textparser(course_id):

    rawtext = retreivecoursetext(course_id)
    rawtext += '|'
    rawtext = (rawtext.replace(' |', ''))
    m = Mystem()
    parsedtext = ''.join(m.lemmatize(rawtext))
    parsedwords = re.split(' |; |, |\*|\n', parsedtext)
    parsedwords.remove('')
    words_counter = Counter(parsedwords)
    return words_counter.most_common(10)


def wordscount(course_id):

    rawtext = retreivecoursetext(course_id)
    if rawtext == "":
        return 0
    rawtext += '|'
    rawtext = (rawtext.replace(' |', ''))
    m = Mystem()
    parsedtext = ''.join(m.lemmatize(rawtext))
    parsedwords = re.split(' |; |, |\*|\n', parsedtext)
    parsedwords.remove('')
    total_words_count = len(parsedwords)
    return total_words_count


def retreivecoursetext(course_id):

    course_activities = Activities.query.filter_by(a_course_id=course_id).order_by(Activities.date.desc()).all()
    course_comments = db.session.query(Groups.group_id, Groups.group_name, Users.user_id, Users.surname, Users.name,
                                       Users.patronymic, Users.u_group_id, CourseComments.user_comment, CourseComments.date,
                                       UserCourses.uc_user_role).filter(Users.user_id == UserCourses.uc_user_id,
                                                                        UserCourses.uc_course_id == course_id,
                                                                        Users.user_id == CourseComments.c_user_id,
                                                                        CourseComments.c_course_id == course_id,
                                                                        Groups.group_id == Users.u_group_id).all()

    course_text = ""
    for c_comment in course_comments:
        course_text = course_text + c_comment.user_comment + " "
    for c_activity in course_activities:
        c_activity_comments = db.session.query(Groups.group_id, Groups.group_name, Users.user_id, Users.surname,
                                               Users.name,
                                               Users.patronymic, Users.u_group_id, Comments.user_comment, Comments.date,
                                               UserCourses.uc_user_role).filter(Users.user_id == UserCourses.uc_user_id,
                                                                                UserCourses.uc_course_id == course_id,
                                                                                Users.user_id == Comments.c_user_id,
                                                                                Comments.c_activity_id == c_activity.activity_id,
                                                                                Groups.group_id == Users.u_group_id).all()
        for c_activity_comment in c_activity_comments:
            course_text = course_text + c_activity_comment.user_comment + " "

    course_text = course_text.lower()
    rawwords = re.findall('[а-яёa-z]+', course_text)
    rawtext = ""
    for rawword in rawwords:
        rawtext = rawtext + rawword + ' '
    return rawtext


@itapp.route('/logout')
def logout():
    logout_user()
    return redirect('main')


@itapp.route('/', methods=['POST', 'GET'])
@itapp.route('/index', methods=['POST', 'GET'])
@itapp.route('/home', methods=['POST', 'GET'])
@itapp.route('/main', methods=['POST', 'GET'])
def index():
    global current_page
    current_page = "main"
    all_faculties = Faculties.query.order_by(Faculties.faculty_name).all()
    all_departments = Departments.query.order_by(Departments.department_name).all()

    u_courses = "NaN"
    p_courses = "NaN"
    if current_user.is_authenticated:
        u_courses = Intensives.query.filter_by(m_course_creator=current_user.user_id).group_by(Intensives.m_course_id).all()
        p_courses = db.session.query(Intensives.m_course_id, Intensives.m_course_name, Intensives.m_course_description,
                                     Intensives.m_course_creator, UserCourses.uc_user_role, Courses.course_id,
                                     Courses.main_course).filter(and_(Intensives.m_course_id == Courses.main_course,
                                                                      UserCourses.uc_course_id == Courses.course_id,
                                                                      UserCourses.uc_user_id == current_user.user_id,
                                                                      Intensives.m_course_creator != current_user.user_id)).group_by(Intensives.m_course_id).all()

    if request.method == 'POST':
        search_course = request.form['search_course'] + "%"
        search_string = search_course.replace(' ', '').replace(',', '').replace('.', '').replace(':', '').replace(';', '').replace('?', '').replace('!', '').replace('-', '')

        return redirect('/search=' + search_string)
    else:
        return render_template("mainpage.html", u_courses=u_courses, p_courses=p_courses, all_faculties=all_faculties, all_departments=all_departments, current_user=current_user, current_page=current_page)


@itapp.route('/secretadmin-addfaculty', methods=['POST', 'GET'])
@login_required
def addfaculty():
    global current_page
    current_page = "notmain"
    if request.method == 'POST':
        faculty_name = request.form['faculty_name']

        currentfaculty = Faculties.query.filter_by(faculty_name=faculty_name).first()

        if currentfaculty is not None:
            flash('This faculty already exists!')
            return redirect('/secretadmin-addfaculty')
        else:
            newfaculty = Faculties()
            newfaculty.faculty_name = faculty_name
            try:
                db.session.add(newfaculty)
                db.session.commit()
                return redirect('/secretadmin-settings')
            except:
                return render_template("newfaculty.html", current_user=current_user, current_page=current_page)
    else:
        return render_template("newfaculty.html", current_user=current_user, current_page=current_page)


@itapp.route('/faculty=<int:faculty_id>-secretadmin-adddepartment', methods=['POST', 'GET'])
@login_required
def adddepartment(faculty_id):
    global current_page
    current_page = "notmain"
    all_faculties = Faculties.query.order_by(Faculties.faculty_name).all()
    if request.method == 'POST':
        department_name = request.form['department_name']
        d_faculty_id = faculty_id

        currentdepartment = Departments.query.filter_by(department_name=department_name).first()

        if currentdepartment is not None:
            flash('This department already exists!')
            return redirect('/faculty=' + str(faculty_id) + '-secretadmin-adddepartment')
        else:
            newdepartment = Departments()
            newdepartment.department_name = department_name
            newdepartment.d_faculty_id = d_faculty_id
            try:
                db.session.add(newdepartment)
                db.session.commit()
                return redirect('/secretadmin-settings')
            except:
                return render_template("newdepartment.html", current_user=current_user, all_faculties=all_faculties, current_page=current_page)
    else:
        return render_template("newdepartment.html", current_user=current_user, all_faculties=all_faculties, current_page=current_page)


@itapp.route('/faculty=<int:faculty_id>-department=<int:department_id>-secretadmin-addgroup', methods=['POST', 'GET'])
@login_required
def addgroup(faculty_id, department_id):
    global current_page
    current_page = "notmain"
    all_departments = Departments.query.filter_by(d_faculty_id=faculty_id).all()
    if request.method == 'POST':
        group_name = request.form['group_name']

        g_department_id = department_id

        currentgroup = Groups.query.filter_by(group_name=group_name).first()

        if currentgroup is not None:
            flash('This group already exists!')
            return redirect('/faculty=' + str(faculty_id) + '-department=' + str(department_id) + '-secretadmin-addgroup')
        else:
            newgroup = Groups()
            newgroup.group_name = group_name
            newgroup.g_department_id = g_department_id
            try:
                db.session.add(newgroup)
                db.session.commit()
                return redirect('/faculty=' + str(faculty_id) + '-department=' + str(department_id))
            except:
                return render_template("newgroup.html", all_departments=all_departments, current_user=current_user, current_page=current_page)
    else:
        return render_template("newgroup.html", all_departments=all_departments, current_user=current_user, current_page=current_page)


current_page = "main"


@itapp.route('/signup', methods=['POST', 'GET'])
def reg():
    global current_page
    current_page = "notmain"
    all_groups = Groups.query.order_by(Groups.group_name).all()
    if request.method == 'POST':
        reg_answer = signup()
        if reg_answer == 0:
            flash('Пользователь с таким именем уже зарегистрирован!')
            return redirect('/signup')
        else:
            return redirect('/login')
    return render_template("reg.html", all_groups=all_groups, current_page=current_page)


@itapp.route('/login', methods=['POST', 'GET'])
def auth():
    global current_page
    current_page = "notmain"
    if request.method == 'POST':
        auth_answer = login()
        if auth_answer == 0:
            flash('Введены некорректные данные!')
            return redirect('/login')
        elif auth_answer == -1:
            flash('В данный момент администратор проверяет Вашу заявку на регистрацию. Ожидайте.')
            return redirect('/login')
        else:
            return redirect('/main')
    return render_template("auth.html", current_page=current_page)


if __name__ == '__main__':
    itapp.run(debug=True)