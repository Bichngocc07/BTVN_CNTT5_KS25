from fastapi.testclient import TestClient
from app import app, service

client = TestClient(app)

def setup_function():
    """Reset CSDL giả lập trước mỗi test case"""
    service.students = {
        "SV001": {
            "student_id": "SV001",
            "student_code": "SV001",
            "name": "Nguyen Van A",
            "full_name": "Nguyen Van A",
            "email": "a.nguyen@gmail.com",
            "age": 20,
            "is_active": True
        }
    }

def test_1_create_student_success():
    """Test 1: Thêm sinh viên thành công -> Tra về 201 Created"""
    payload = {
        "student_code": "SV003",
        "full_name": "Bich Ngoc",
        "email": "ngoc.bich@gmail.com",
        "age": 20,
        "is_active": True
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    assert response.json()["student_code"] == "SV003"

def test_2_duplicate_code_and_email():
    """Test 2: Chặn trùng Mã SV hoặc trùng Email -> Trả về 400 Bad Request"""
    # Trùng Mã
    res_code = client.post("/students", json={
        "student_code": "SV001",
        "full_name": "Tran Van B",
        "email": "b.tran@gmail.com",
        "age": 22,
        "is_active": True
    })
    assert res_code.status_code == 400

    # Trùng Email
    res_email = client.post("/students", json={
        "student_code": "SV099",
        "full_name": "Nguyen Van C",
        "email": "a.nguyen@gmail.com",
        "age": 23,
        "is_active": True
    })
    assert res_email.status_code == 400

def test_3_blank_code_or_name():
    """Test 3: Chặn mã hoặc tên rỗng -> Trả về 422 Unprocessable Entity"""
    response = client.post("/students", json={
        "student_code": "   ",
        "full_name": "   ",
        "email": "valid@gmail.com",
        "age": 20,
        "is_active": True
    })
    assert response.status_code == 422

def test_4_invalid_age():
    """Test 4: Chặn tuổi ngoài 18-60 -> Trả về 422 Unprocessable Entity"""
    res_young = client.post("/students", json={
        "student_code": "SV004", "full_name": "Young", "email": "y@gmail.com", "age": 17, "is_active": True
    })
    assert res_young.status_code == 422

    res_old = client.post("/students", json={
        "student_code": "SV005", "full_name": "Old", "email": "o@gmail.com", "age": 65, "is_active": True
    })
    assert res_old.status_code == 422

def test_5_invalid_email_format():
    """Test 5: Chặn Email sai định dạng -> Trả về 422 Unprocessable Entity"""
    response = client.post("/students", json={
        "student_code": "SV006",
        "full_name": "Test User",
        "email": "sai_email.com",
        "age": 25,
        "is_active": True
    })
    assert response.status_code == 422