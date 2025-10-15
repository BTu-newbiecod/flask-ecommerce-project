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

5.  **Chạy ứng dụng:**
    ```bash
    flask run
    ```

---

