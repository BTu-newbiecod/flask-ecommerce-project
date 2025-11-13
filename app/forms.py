from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField,FloatField,IntegerField
from wtforms.validators import DataRequired,Length,Email,EqualTo,NumberRange,ValidationError
from flask_login import current_user
from app.models import User

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

class EditProfileForm(FlaskForm):
    username = StringField('Tên đăng nhập',validators=[DataRequired(), Length(min=4, max=64)])
    
    email = StringField('Email',validators=[DataRequired(), Email()])

    submit = SubmitField('Cập nhật hồ sơ')

    #kiểm tra xem username mới có bị trùng không
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Tên đăng nhập này đã có người sử dụng.')
    #kiểm tra xem email mới có bị trùng không
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email này đã có người sử dụng.')
            
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Mật khẩu hiện tại', validators=[DataRequired()])
    
    new_password = PasswordField('Mật khẩu mới', validators=[DataRequired(), Length(min=6)])
    
    confirm_password = PasswordField('Xác nhận mật khẩu mới', validators=[DataRequired(), EqualTo('new_password', message='Mật khẩu không khớp.')])
    
    submit = SubmitField('Đổi mật khẩu')

    # Hàm kiểm tra mật khẩu cũ có đúng không
    def validate_old_password(self, old_password):
        if not current_user.check_password(old_password.data):
            raise ValidationError('Mật khẩu hiện tại không đúng.')
        
class AddressForm(FlaskForm):
    recipient_name = StringField('Họ và tên người nhận',validators=[DataRequired(), Length(max=100)])
    
    phone_number = StringField('Số điện thoại', validators=[DataRequired(), Length(max=20)])
    
    street_address = TextAreaField('Địa chỉ chi tiết (Số nhà, đường, phường/xã)', validators=[DataRequired(), Length(max=255)])
    
    city = StringField('Tỉnh / Thành phố', validators=[DataRequired(), Length(max=100)])
    
    is_default = BooleanField('Đặt làm địa chỉ mặc định')
    
    submit = SubmitField('Lưu Địa Chỉ')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Gửi yêu cầu reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Mật khẩu mới', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password', message='Mật khẩu không khớp.')])
    submit = SubmitField('Đặt lại mật khẩu')