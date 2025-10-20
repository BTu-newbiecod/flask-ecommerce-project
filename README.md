#  Dự án Website E-commerce & Chatbot AI

Dự án xây dựng một website bán hàng trực tuyến sử dụng Flask, tích hợp chatbot AI (Gemini) để hỗ trợ khách hàng.

## Thành viên nhóm

* **Nguyễn Đình Đạt**
* **Lê Minh Phương** 
* **Lê Thành Thông** 
* **Nguyễn Bá Tú** 

---

##  Công nghệ sử dụng

* **Backend:** Python, Flask, Flask-SQLAlchemy
* **Cơ sở dữ liệu:** SQLite
* **AI Chatbot:** Google Gemini API
* **Quản lý code:** Git & GitHub

---

## Cấu trúc dự án
```
flask-ecommerce-project/
├── app/                  # ứng dụng chính
│   ├── __init__.py       # Khởi tạo app và đăng ký Blueprints
│   ├── models.py     
│   ├── forms.py          
│   │
│   ├── static/        
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── images/
│   │
│   ├── templates/     
│   │   ├── base.html     
│   │   ├── index.html   
│   │   │
│   │   ├── auth/         
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   │
│   │   └── admin/        
│   │       ├── admin_base.html
│   │       └── products.html
│   │
│   ├── main/             # --- Blueprint cho các trang chính ---
│   │   ├── __init__.py   # tạo blueprint 'main'
│   │   └── routes.py     # Các route cho trang chủ, chi tiết sản phẩm,...
│   │
│   ├── auth/             # --- Blueprint cho xác thực người dùng ---
│   │   ├── __init__.py   # tạo blueprint 'auth'
│   │   └── routes.py     # Các route cho login, logout, register,...
│   │
│   └── admin/            # --- Blueprint cho trang quản trị ---
│       ├── __init__.py   # tạo blueprint 'admin'
│       └── routes.py     # Các route cho quản lý sản phẩm, đơn hàng,...
│
├── migrations/        
├── venv/                 
│
├── .gitignore           
├── config.py            
├── README.md             # Tài liệu hướng dẫn dự án
├── requirements.txt      # Danh sách các thư viện cần cài đặt
├── run.py                # File để chạy ứng dụng
└── seed.py               # tạo dữ liệu mẫu
```

---

##  Hướng dẫn cài đặt

1.  **Lấy code về máy (Clone):**
    ```bash
    git clone <URL_REPO_SE_DUOC_TAO_SAU_DAY>
    ```

2.  **Tạo và kích hoạt môi trường ảo:**
    ```bash ( trong terminal ở VSCODE )
    cd tên dự án
    gõ: python -m venv venv (để tạo mt ảo, tất cả thiết lập chỉ có trong mt ảo, ko ảnh hưởng đến bên ngoài)
    gõ: .\venv\Scripts\activate (kích hoạt mt ảo)
    ```

3.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Tạo cơ sở dữ liệu cục bộ:**
    ```bash
    set FLASK_APP=run.py
    flask db upgrade
    ```

5. **Chèn dữ liệu mẫu:**
    ```bash
    Gõ: python seed.py
    
    Sau khi chạy xong, file app.db trên máy của mọi người sẽ có đầy đủ dữ liệu để bắt đầu code giao diện và các tính năng khác.
    ```


6.  **Chạy ứng dụng:**
    ```bash
    flask run
    ```

---

