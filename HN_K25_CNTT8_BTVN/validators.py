import re

def is_valid_student_id(student_id: str, existing_ids: set = None) -> tuple[bool, str]:
    """Kiểm tra mã sinh viên: Không được rỗng và không trùng lặp."""
    student_id = student_id.strip()
    if not student_id:
        return False, "Mã sinh viên không được để rỗng!"
    if existing_ids and student_id in existing_ids:
        return False, f"Mã sinh viên '{student_id}' đã tồn tại trong hệ thống!"
    return True, ""

def is_valid_name(name: str) -> tuple[bool, str]:
    """Kiểm tra tên sinh viên: Không được chỉ có khoảng trắng hoặc rỗng."""
    if not name or not name.strip():
        return False, "Tên sinh viên không được để rỗng hoặc chỉ chứa khoảng trắng!"
    return True, ""

def is_valid_email(email: str, existing_emails: set = None) -> tuple[bool, str]:
    """Kiểm tra email: Đúng định dạng regex và không trùng lặp."""
    email = email.strip()
    if not email:
        return False, "Email không được để rỗng!"
    
    # Định dạng email chuẩn cơ bản
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Email không đúng định dạng (VD: example@domain.com)!"
    
    if existing_emails and email in existing_emails:
        return False, f"Email '{email}' đã tồn tại trong hệ thống!"
    return True, ""

def is_valid_age(age_input) -> tuple[bool, str, int]:
    """Kiểm tra tuổi: Phải là số nguyên hợp lệ trong khoảng 17-100."""
    try:
        age = int(age_input)
        if age < 17 or age > 100:
            return False, "Tuổi phải là số nguyên từ 17 đến 100!", None
        return True, "", age
    except (ValueError, TypeError):
        return False, "Tuổi phải là một số nguyên hợp lệ!", None