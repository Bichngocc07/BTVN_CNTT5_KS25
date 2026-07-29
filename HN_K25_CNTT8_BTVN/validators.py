import re

def is_valid_student_id(student_id: str, existing_ids: set = None) -> tuple[bool, str]:
    """Kiểm tra mã sinh viên: Bắt buộc định dạng SVxxx (VD: SV001), không rỗng, không trùng."""
    student_id = student_id.strip()
    if not student_id:
        return False, "Mã sinh viên không được để rỗng!"
    
    # Quy tắc Validation: Mã phải bắt đầu bằng SV và theo sau là các chữ số
    pattern = r"^SV\d+$"
    if not re.match(pattern, student_id):
        return False, "Mã sinh viên phải có định dạng 'SV' + chữ số (Ví dụ: SV001, SV002)!"

    if existing_ids and student_id in existing_ids:
        return False, f"Mã sinh viên '{student_id}' đã tồn tại trong hệ thống!"
    return True, ""

def is_valid_name(name: str) -> tuple[bool, str]:
    """Kiểm tra tên sinh viên: Không được rỗng hoặc chỉ chứa khoảng trắng."""
    if not name or not name.strip():
        return False, "Tên sinh viên không được để rỗng hoặc chỉ chứa khoảng trắng!"
    return True, ""

def is_valid_email(email: str, existing_emails: set = None) -> tuple[bool, str]:
    """Kiểm tra email: Đúng định dạng regex và không trùng lặp."""
    email = email.strip()
    if not email:
        return False, "Email không được để rỗng!"
    
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Email không đúng định dạng (VD: example@domain.com)!"
    
    if existing_emails and email in existing_emails:
        return False, f"Email '{email}' đã tồn tại trong hệ thống!"
    return True, ""

def is_valid_age(age_input) -> tuple[bool, str, int | None]:
    """Kiểm tra tuổi: Phải là số nguyên từ 17 đến 100."""
    try:
        age = int(age_input)
        if age < 17 or age > 100:
            return False, "Tuổi phải là số nguyên từ 17 đến 100!", None
        return True, "", age
    except (ValueError, TypeError):
        return False, "Tuổi phải là một số nguyên hợp lệ!", None
