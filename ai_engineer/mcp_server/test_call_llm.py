import requests
import json

# Định nghĩa URL của API
url = "http://localhost:8000/ai_chat/query_understand/"

# Headers yêu cầu (tương đương với -H trong curl)
headers = {
    "accept": "*/*",
    "Content-Type": "application/json"
}

# Dữ liệu gửi đi dạng dictionary (tương đương với -d trong curl)
payload = {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "content": "Kha Banh La ai ",
    "question_context": None
}

try:
    # Thực hiện gửi request POST
    response = requests.post(url, headers=headers, json=payload)
    
    # Kiểm tra mã trạng thái HTTP (200 là thành công)
    if response.status_code == 200:
        print("Thành công!")
        # In kết quả trả về dạng JSON
        print(response.json())
    else:
        print(f"Lỗi! Mã trạng thái: {response.status_code}")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"Đã xảy ra lỗi kết nối: {e}")