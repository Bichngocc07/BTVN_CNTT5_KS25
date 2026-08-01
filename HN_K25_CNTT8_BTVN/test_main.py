from fastapi.testclient import TestClient
from app import app, db_students

client = TestClient(app)

def setup_function():
    """Reset dữ liệu giả lập trong list trước mỗi test case"""
    db_students.clear()
    db_students.extend([
        {
            "student_code": "SV001",
            "full_name": "Nguyen Van A",
            "email": "a.nguyen@gmail.com",
            "age": 20,
            "is_active": True
        },
        {
            "student_code": "SV002",
            "full_name": "Tran Thi B",
            "email": "b.tran@gmail.com",
            "age": 22,
            "is_active": True
        }
    ])

def test_1_get_all_students():
    """Test Lấy danh sách tất cả sinh viên -> 200 OK"""
    res = client.get("/students")
    assert res.status_code == 200
    assert len(res.json()) == 2

def test_2_get_student_by_id_success_and_404():
    """Test Lấy chi tiết sinh viên (Thành công 200 OK & Lỗi 404 Not Found)"""
    # Thành công
    res_ok = client.get("/students/SV001")
    assert res_ok.status_code == 200
    assert res_ok.json()["full_name"] == "Nguyen Van A"

    # Lỗi 404 khi ID không tồn tại
    res_fail = client.get("/students/SV999")
    assert res_fail.status_code == 404

def test_3_create_student_success():
    """Test Thêm sinh viên thành công -> 201 Created"""
    payload = {
        "student_code": "SV003",
        "full_name": "Le Van C",
        "email": "c.le@gmail.com",
        "age": 21,
        "is_active": True
    }
    res = client.post("/students", json=payload)
    assert res.status_code == 201
    assert res.json()["student_code"] == "SV003"
    assert len(db_students) == 3

def test_4_create_student_duplicate_email_or_code():
    """Test Chặn trùng Mã SV hoặc trùng Email -> 400 Bad Request"""
    # Trùng Code
    res_code = client.post("/students", json={
        "student_code": "SV001",
        "full_name": "Trung Code",
        "email": "unique@gmail.com",
        "age": 20,
        "is_active": True
    })
    assert res_code.status_code == 400

    # Trùng Email
    res_email = client.post("/students", json={
        "student_code": "SV004",
        "full_name": "Trung Email",
        "email": "a.nguyen@gmail.com",
        "age": 20,
        "is_active": True
    })
    assert res_email.status_code == 400

def test_5_put_update_student_success_and_404():
    """Test Cập nhật toàn bộ (PUT) thành công -> 200 OK & 404 Not Found"""
    payload = {
        "full_name": "Nguyen Van A Updated",
        "email": "a.updated@gmail.com",
        "age": 25,
        "is_active": False
    }
    res = client.put("/students/SV001", json=payload)
    assert res.status_code == 200
    assert res.json()["full_name"] == "Nguyen Van A Updated"

    # Sửa ID không tồn tại -> 404
    res_404 = client.put("/students/SV999", json=payload)
    assert res_404.status_code == 404

def test_6_patch_update_student():
    """Test Cập nhật một phần (PATCH) -> 200 OK"""
    payload = {"age": 29}
    res = client.patch("/students/SV001", json=payload)
    assert res.status_code == 200
    assert res.json()["age"] == 29
    assert res.json()["full_name"] == "Nguyen Van A"  # Giữ nguyên các trường khác

def test_7_delete_student_success_and_404():
    """Test Xóa sinh viên -> 200 OK & 404 Not Found"""
    # Xóa thành công
    res = client.delete("/students/SV001")
    assert res.status_code == 200
    assert len(db_students) == 1

    # Xóa lại ID vừa xóa -> 404
    res_404 = client.delete("/students/SV001")
    assert res_404.status_code == 404

def test_8_validation_errors():
    """Test Dữ liệu không hợp lệ (Mã/Tên rỗng, tuổi ngoài khoảng) -> 422 Unprocessable Entity"""
    res = client.post("/students", json={
        "student_code": "   ",
        "full_name": "Valid Name",
        "email": "valid@gmail.com",
        "age": 10,  # Tuổi < 18
        "is_active": True
    })
    assert res.status_code == 422
