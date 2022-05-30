from flask import request
from sqlalchemy import exc

from flask_login import login_user

from soup import db, Groups, Users


def signup():
    user_login = request.form['user_login']
    user_password = request.form['user_password']
    name = request.form['name']
    surname = request.form['surname']
    patronymic = request.form['patronymic']
    mail = request.form['mail']
    selected_professor = request.form.getlist('Professor')
    selected_student = request.form.getlist('Student')
    u_group_id = 0
    if bool(selected_professor):
        u_group_id = 2
    elif bool(selected_student):
        u_group_id = Groups.query.filter_by(group_name=request.form['user_group']).first().group_id

    currentuser = Users.query.filter_by(user_login=user_login).first()

    if currentuser is not None:
        return 0
    else:
        newuser = Users()
        if user_login == 'Cinemancer':
            u_group_id = 1
            newgroup = Groups()
            newgroup.group_name = 'Администратор'
            newgroup.g_department_id = 0
            db.session.add(newgroup)
            db.session.commit()
            newgroup = Groups()
            newgroup.group_name = 'Преподаватель'
            newgroup.g_department_id = 0
            db.session.add(newgroup)
            db.session.commit()
            newgroup = Groups()
            newgroup.group_name = 'Неверифицированный пользователь'
            newgroup.g_department_id = 0
            db.session.add(newgroup)
            db.session.commit()
        newuser.user_login = user_login
        newuser.set_password(user_password)
        newuser.name = name
        newuser.surname = surname
        newuser.patronymic = patronymic
        newuser.mail = mail
        if u_group_id != 2:
            newuser.u_group_id = u_group_id
        else:
            newuser.u_group_id = 3
        try:
            db.session.add(newuser)
            db.session.commit()
            return 1
        except exc.SQLAlchemyError as e:
            return "e"


def login():
    user_login = request.form['user_login']
    user_password = request.form['user_password']
    currentuser = Users.query.filter_by(user_login=user_login).first()
    verifyinguser = Users.query.filter_by(user_login=user_login, u_group_id=3).first()
    if currentuser is None and verifyinguser is None:
        return 0
    elif currentuser is not None and not currentuser.check_password(user_password):
        return 0
    elif currentuser is not None and verifyinguser is not None:
        return -1
    else:
        login_user(currentuser, remember=True)
        return 1