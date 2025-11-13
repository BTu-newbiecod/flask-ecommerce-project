from flask_login import login_required, login_user, logout_user
from flask import flash, redirect, render_template, url_for
from app.forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
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
        
        user=User(
            username=form.username.data, 
            email=form.email.data,
            password=form.password.data
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
        if user is None:
            flash('Email này chưa có trong hệ thống. Vui lòng đăng ký tài khoản!', 'warning')
            return redirect(url_for('auth.register'))
        elif user.password != form.password.data:
            token = user.get_reset_token()
            flash('Mật khẩu không đúng. Bạn có thể đặt lại mật khẩu.', 'info')
            return redirect(url_for('auth.reset_password', token=token))
        
        login_user(user)#HÀM THÔNG MINH CỦA FLASK_LOGIN, giúp quản lý session
        flash('Đăng nhập thành công! Chào mừng bạn đến Pypy Store','success')
        if user.email == "admin@shop.com":
            return redirect(url_for('admin.dashboard'))  
        else:
            return redirect(url_for('main.index'))  

    return render_template('auth/login.html',form=form)

@bp.route('/logout',methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất','info')
    return redirect(url_for('main.index'))#CHU Y

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@shop.com':
            flash('Admin không được thay đổi mật khẩu!', 'danger')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_reset_token()
            return redirect(url_for('auth.reset_password', token=token))
        else:
            flash('Email này chưa có trong hệ thống. Vui lòng đăng ký tài khoản!', 'warning')
            return redirect(url_for('auth.register'))
    return render_template('auth/forgot_password.html', form=form)

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('Token không hợp lệ hoặc đã hết hạn.', 'danger')
        return redirect(url_for('auth.login'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Mật khẩu của bạn đã được đặt lại thành công!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

