from datetime import datetime


def check_monday():
    """
        Check whether today is Monday or not
    """
    # Lấy ngày giờ hiện tại
    today = datetime.now()
    
    # weekday() trả về số từ 0 (Thứ Hai) đến 6 (Chủ Nhật)
    return today.weekday() == 0
