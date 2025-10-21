from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash,check_password_hash
from flask import flash, redirect, render_template, url_for
from app.forms import RegistrationForm,LoginForm
from app.models import User
from app import db
from app.auth import bp


@bp.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm() #khoi tao doi tuong form
    if(form.validate_on_submit()): #kiểm tra xem PT POST và tất cả dữ liệu người dùng gửi lên có vượt qua được các validators cua form
        if(User.query.filter_by(email=form.email.data).first()): #kiem tra email da ton tai?
            flash('Email đã được sử dụng','danger')
            return redirect(url_for('auth.register'))
        
        if(User.query.filter_by(username=form.username.data).first()):
            flash('Username đã tồn tại','danger')
            return redirect(url_for('auth.register'))
       
        hash_password=generate_password_hash(form.password.data) #ma hoa mk
        
        user=User(
            username=form.username.data, 
            email=form.email.data,
            password=hash_password
        )

        db.session.add(user)
        db.session.commit()
        flash('Bạn đã đăng ký thành công! Hãy đăng nhập','success')
        return redirect(url_for('auth.login'))
    
    #neu la GET TUC NHAP 
    return render_template('auth/register.html',form=form)

@bp.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if(form.validate_on_submit()):
        user=User.query.filter_by(email=form.email.data).first()
        if(user is None or not check_password_hash(user.password,form.password.data)):
            flash('Sai email hoặc mật khẩu','danger')
            return redirect(url_for('auth.login'))
        
        login_user(user)#HÀM THÔNG MINH CỦA FLASK_LOGIN, giúp quản lý session
        flash('Đăng nhập thành công! Chào mừng bạn đến ONLINE-SHOP','success')
        return redirect(url_for('main.index')) #CHU Y

    return render_template('auth/login.html',form=form)

@bp.route('/logout',method=['GET'])
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất','info')
    return redirect(url_for('main.index'))#CHU Y
    
