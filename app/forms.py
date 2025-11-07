from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField,FloatField,IntegerField
from wtforms.validators import DataRequired,Length,Email,EqualTo,NumberRange

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

class ProductForm(FlaskForm):
    name = StringField('Tên sản phẩm', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Mô tả sản phẩm')
    price = FloatField('Giá', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Tồn kho', validators=[DataRequired(), NumberRange(min=0)])
    img_file = StringField('Tên file ảnh')
    submit = SubmitField('Lưu')
    pass