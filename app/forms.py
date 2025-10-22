from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired,Length,Email,EqualTo

class LoginForm(FlaskForm):
    email=StringField('email',validators=[DataRequired(),Email()])
    password= PasswordField('Mật khẩu',validators=[DataRequired(),Length(min=6,max=100)])
    submit=SubmitField('Đăng nhập')
    remember_me = BooleanField('Ghi nhớ đăng nhập')
    pass

class RegistrationForm(FlaskForm):
    username=StringField('Tên đăng nhâp',validators=[DataRequired(),Length(max=30)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password= PasswordField('Mật khẩu',validators=[DataRequired(),Length(min=6,max=100)])
    confirm_password=PasswordField('Xác nhận mật khẩu',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Đăng ký')
    pass