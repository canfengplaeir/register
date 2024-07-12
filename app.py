from flask import Flask, flash, redirect, request, url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user
from flask_login import UserMixin
from flask_login import login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

class Config(object):
    """配置参数"""
    # 设置连接数据库的URL
    user = 'root'
    password = '123456'
    database = 'test'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@127.0.0.1:3306/%s' % (user,password,database)

    # 设置sqlalchemy自动更跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 查询时会显示原始SQL语句
    app.config['SQLALCHEMY_ECHO'] = True

    # 禁止自动提交数据处理
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False

# 读取配置
app.config.from_object(Config)

db = SQLAlchemy(app)


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    course_name = db.Column(db.String(64), unique=True)
    course_id = db.Column(db.String(64), unique=True)

class Teacher(db.Model):
    __tablename__ = 'teacher'
    tid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    teacher = db.Column(db.String(64), unique=True)
    teacher_introduce = db.Column(db.String(64), unique=True)
    teacher_img_url = db.Column(db.String(64), unique=True)

@app.route('/get/<id>',methods=['GET'])
def getCourseInfo(id):
    course = Course.query.get(id)

    return f'名称:{course.course_name}，id是{course.course_id}'



@app.route('/')
def main():
    return render_template('main.html')

@app.route("/register")
def MakeAnAppointmentToRegister():
    metaInformation = Course.query.all()
    metaInformation_count = Course.query.count()
    return render_template('register.html',metaInformation=metaInformation,metaInformation_count = metaInformation_count)

@app.route("/404" , endpoint="404")
def page404():
    return render_template('404.html')

@app.route("/register/chooseteacher/<id>")
def Chooseteacher(id):
    class course_teacher(db.Model):
            __table_args__ = {'extend_existing': True}
            __tablename__ = 'course_teacher_' + id
            tid = db.Column(db.Integer, primary_key=True,autoincrement=True)
            teacher = db.Column(db.String(64), unique=True)
            teacher_introduce = db.Column(db.String(64), unique=True)
            teacher_img_url = db.Column(db.String(64), unique=True)
    teacher_info = course_teacher.query.all()
    tid_count = course_teacher.query.count()#INT
    # teacher_info = []
    # for i in range(tid_count):
    #     teacher_info.append(Teacher.query.get(tidGet[i].tid))
    return render_template('chooseteacher.html',teacher_info=teacher_info,tid_count=tid_count)

@app.route("/register/chooseteacher/<id>/<tid>")
def SelectCourse(id,tid):
    class course_teacher_class(db.Model):
            __table_args__ = {'extend_existing': True}
            __tablename__ = 'course_teacher_' + id + "_" + tid # type: ignore
            class_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
            class_name = db.Column(db.String(64), unique=True)
            class_num = db.Column(db.String(64), unique=True)
            class_time = db.Column(db.String(64), unique=True)

    class course_teacher(db.Model):
            __table_args__ = {'extend_existing': True}
            __tablename__ = 'course_teacher_' + id
            tid = db.Column(db.Integer, primary_key=True,autoincrement=True)
            teacher = db.Column(db.String(64), unique=True)
            teacher_introduce = db.Column(db.String(64), unique=True)
            teacher_img_url = db.Column(db.String(64), unique=True)
    class_info = course_teacher_class.query.all()
    teacher_info = course_teacher.query.all()
    teacher_img = teacher_info[int(tid)- 1].teacher_img_url
    class_count = course_teacher_class.query.count()
    return render_template('chooseclass.html',class_info = class_info,class_count= class_count,teacher_img=teacher_img)

#表格
    
@app.route("/form")
def FillOutForm():
     return render_template("form.html")

class User(db.Model,UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(20))
    name = db.Column(db.String(20))  # 用户名
    password = db.Column(db.String(128)) 
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值

login_manager = LoginManager(app)  # 实例化扩展类

@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']

        if not name or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        hash = generate_password_hash("12345678")
        print('我草泥马',hash)
        user = User.query.first()
        print(user.name , user.password_hash , user.password)
        # 验证用户名和密码是否一致
        if name == user.name and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')  
        else:
            flash('验证失败')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')

@app.route('/logout')
@login_required  # 
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('main'))  # 重定向回首页

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
    