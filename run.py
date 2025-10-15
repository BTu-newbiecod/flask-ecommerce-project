
from app import create_app #Ham tao app hoan chinh

app = create_app() #Goi ham

#Khởi động máy chủ
if __name__ == '__main__':
    app.run(debug=True)