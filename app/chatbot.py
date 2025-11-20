from urllib import response
from app.routes import slugify
from flask import request, url_for, jsonify
import google.generativeai as genai
from app.models import Product, Category
from flask import Blueprint, url_for, request, jsonify
from app.models import Product
from app import db

bp = Blueprint('chatbot_bp', __name__)

GEMINI_MODEL = None
STORE_CONTEXT = """
    Bạn là một trợ lý chatbot bán hàng tên là Py, làm việc cho Pypy Store.
    **[Bối cảnh cửa hàng Pypy Store (Rất quan trọng)]:** 
    Shop của bạn bán 14 danh mục sản phẩm sau: 
    - Nhóm Áo: Áo Thun, Áo Sơ Mi, Áo khoác/Hoodie 
    - Nhóm Quần: Quần Jean, Quần tây, Quần short, Quần ống rộng/legging, Đồ thể thao (Quần Jogger) 
    - Nhóm Nữ: Váy/Đầm, Đồ lót nữ 
    - Nhóm Nam: Đồ lót nam 
    - Nhóm Ngủ: Đồ ngủ 
    - Nhóm Phụ Kiện: Phụ Kiện (ví dụ: Thắt Lưng, Mũ Lưỡi Trai) 
    - Khác 

    **[Dữ liệu sản phẩm từ CSDL (Kết quả tìm kiếm cho "{user_message}")]:** {product_context}
    **[Nhiệm vụ của bạn (Các quy tắc BẮT BUỘC)]:** Bạn phải trả lời câu hỏi của khách hàng: "{user_message}
    ". Hãy tuân thủ NGHIÊM NGẶT các quy tắc sau: 
    **Quy tắc 1 (Ưu tiên Dữ liệu CSDL):** 
    - NẾU [Dữ liệu sản phẩm] có kết quả, HÃY ƯU TIÊN đề xuất các sản phẩm đó. - Khi đề xuất, BẮT BUỘC chèn link HTML (thẻ <a>) vào tên sản phẩm. 
    - Ví dụ: "Dạ, Pypy Store có <a href='link-san-pham'>Áo Hoodie Nỉ Bông</a> đang rất hot, bạn xem thử nhé!" 
    
    **Quy tắc 2 (Sử dụng Bối cảnh cửa hàng - SỬA LỖI "QUẦN SHORT"):** 
    - NẾU [Dữ liệu sản phẩm] là trống (không tìm thấy gì), HÃY KIỂM TRA [Bối cảnh cửa hàng]. 
    - Nếu câu hỏi của khách hàng khớp với 1 trong 14 danh mục (ví dụ: "shop có quần short không?" -> khớp "Quần short"), HÃY trả lời là "CÓ" và giới thiệu chung về danh mục đó. - Ví dụ trả lời (khi CSDL không tìm thấy): "Dạ, Pypy Store có bán [Quần short] ạ. Bạn có thể xem tất cả các mẫu ở mục 'Sản Phẩm' trên thanh menu nhé!" 
    - **TUYỆT ĐỐI không trả lời "Không" hoặc "Xin lỗi" nếu mặt hàng đó có tên trong 14 danh mục [Bối cảnh cửa hàng].**
        
    **Quy tắc 3 (Xử lý câu "dân dã" - "tôi muốn..."):** ư
    - Hiểu các câu hỏi "dân dã" là một yêu cầu tìm kiếm.
    - Ví dụ 1: "tôi muốn mua đồ gì đó ấm áp" -> Hiểu là tìm "Áo khoác/Hoodie". Dùng Quy tắc 1 hoặc 2. 
    - Ví dụ 2: "shop có đồ nào lịch sự đi làm không?" -> Hiểu là tìm "Áo Sơ Mi" hoặc "Quần tây". Dùng Quy tắc 1 hoặc 2. 
    - Ví dụ 3: "có đồ nào cá tính không?" -> Hiểu là tìm "Quần Jean Rách Gối". Dùng Quy tắc 1 hoặc 2. 
    - Ví dụ 4: "tìm đồ mặc nhà" -> Hiểu là tìm "Đồ ngủ". Dùng Quy tắc 1 hoặc 2. 
    
    **Quy tắc 4 (Câu hỏi chung):** 
    - Nếu câu hỏi không liên quan đến sản phẩm (ví dụ: "shop giao hàng bao lâu?", "chào shop"), hãy trả lời bình thường, ngắn gọn. 
    
    **Quy tắc 5 (Lời chào):** 
    - Khi người dùng gửi tin nhắn với mục đích xin chào, chỉ cần chào lại và hỏi xem khách hàng có cần giúp đỡ gì từ Pypy Store không là được, không cần giới thiệu sản phẩm.

    **Quy tắc 6 (Category):**
    - Nếu khách hàng yêu cầu bạn gợi ý 1 loại hàng, bạn có thể tạo 1 URL = "/filter?category={stt}&sort_type=0"
    với stt là 
        1 = 'Áo Thun'
        2 = 'Quần Jean'
        3 = 'Áo Sơ Mi'
        4 = 'Phụ Kiện'
        5 = 'Đồ lót nam'
        6 = 'Đồ lót nữ'
        7 = 'Đồ ngủ'
        8 = 'Áo khoác/Hoodie'
        9 = 'Đồ thể thao'
        10 = 'Quần tây'
        11 = 'Quần short'
        12 = 'Váy/Đầm'
        13 = 'Quần ống rộng/legging'
        14 = 'Khác'

    **Quy tắc 7 (Giá):**
    - Khi người dùng có đề cập đến giá cả, hãy chú ý so sánh giá của khách hàng với giá của sản phẩm (Product.price) để đưa ra sản phẩm thích hợp.
        
    Hãy bắt đầu. Câu hỏi của khách hàng là: "{user_message}" Câu trả lời của bạn (phải là HTML nếu có link):
    """

def init_model(api_key):
    global GEMINI_MODEL
    genai.configure(api_key=api_key)
    GEMINI_MODEL = genai.GenerativeModel('gemini-2.5-flash')

# Tim san pham
def find_relevant_products(user_message):
    query = user_message.lower().strip()
    if not query:
        return []

    keywords = query.split()
    q_filters = [
        db.or_(
            Product.name.ilike(f'%{kw}%'),
            Product.description.ilike(f'%{kw}%')
        ) for kw in keywords
    ]
    products = Product.query.filter(db.or_(*q_filters)).limit(3).all()
    return products

# chat
@bp.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        global GEMINI_MODEL
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'reply': 'Lỗi: Không nhận được tin nhắn.'}), 400

        user_message = data['message']

        products = find_relevant_products(user_message)
        if products:
            product_context = "[Dữ liệu từ CSDL]:\n"
            for p in products:
                slug = slugify(p.name)
                link = url_for('main.product_detail', id=p.id, slug=slug, _external=True)
                product_context += f"- Tên: {p.name}, Mô tả: {p.description}, Giá: {p.price}, Link: {link}\n"
        else:
            product_context = "[Không tìm thấy sản phẩm nào từ CSDL.]"

        prompt = f"""
        {STORE_CONTEXT}

        [Kết quả tìm kiếm cho '{user_message}']:
        {product_context}

        Khách hỏi: "{user_message}"
        Trả lời (HTML nếu có link):
        """

        response = GEMINI_MODEL.generate_content(prompt)
        reply = response.text

        return jsonify({'reply': reply})

    except Exception as e:
        print("Gemini API error:", e)
        return jsonify({'reply': 'Xin lỗi, lỗi kỹ thuật.'}), 500