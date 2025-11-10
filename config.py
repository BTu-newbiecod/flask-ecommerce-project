import os

basedir=os.path.abspath(os.path.dirname(__file__)) #lay ra duong dan den thu muc

class Config:

    #ma hoa session cookies ->tranh lam gia ,tan cong request trang web
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'ban_nen_thay_doi_chuoi_nay'

    SQLAlCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    GEMINI_API_KEY = 'AIzaSyAGWOoFGe3SffZa6MINF0h7ZEl-Aic3E_I'
    
