import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import app
from database import Base, get_db

# Tạo CSDL SQLite in-memory cho mục đích testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# TEST 1: Kiểm tra PUT cập nhật thành công
def test_1_put_update_mysql_student_success():
    # Tạo sinh viên ban đầu
    post_res = client.post("/db/students", json={
        "student_code": "SV001",
        "student_name": "Nguyen Van A",
        "email": "a.nguyen@gmail.com",
        "age": 20
    })
    s_id = post_res.json()["id"]

    # Gọi API PUT
    put_res = client.put(f"/db/students/{s_id}", json={
        "student_code": "SV001_UPDATED",
        "student_name": "Nguyen Van A Updated",
        "email": "a.updated@gmail.com",
        "age": 25,
        "is_active": True
    })

    assert put_res.status_code == 200
    assert put_res.json()["student_name"] == "Nguyen Van A Updated"
    assert put_res.json()["email"] == "a.updated@gmail.com"


# TEST 2: Kiểm tra PUT/PATCH/DELETE trả về 404 khi ID không tồn tại
def test_2_mysql_student_not_found_404():
    res_put = client.put("/db/students/9999", json={
        "student_code": "SV999",
        "student_name": "Non Existent",
        "email": "non@gmail.com",
        "age": 20,
        "is_active": True
    })
    assert res_put.status_code == 404

    res_patch = client.patch("/db/students/9999", json={"age": 30})
    assert res_patch.status_code == 404

    res_delete = client.delete("/db/students/9999")
    assert res_delete.status_code == 404


# TEST 3: Kiểm tra chặn trùng email/student_code khi cập nhật PUT
def test_3_put_duplicate_code_or_email():
    # Tạo 2 sinh viên
    client.post("/db/students", json={
        "student_code": "SV001", "student_name": "SV Một", "email": "sv1@gmail.com"
    })
    s2 = client.post("/db/students", json={
        "student_code": "SV002", "student_name": "SV Hai", "email": "sv2@gmail.com"
    }).json()

    # Thử sửa SV2 với email của SV1 -> Chặn trùng 400
    res_dup = client.put(f"/db/students/{s2['id']}", json={
        "student_code": "SV002",
        "student_name": "SV Hai",
        "email": "sv1@gmail.com",
        "age": 22,
        "is_active": True
    })
    assert res_dup.status_code == 400


# TEST 4: Kiểm tra PATCH cập nhật một phần thành công
def test_4_patch_update_partial_success():
    post_res = client.post("/db/students", json={
        "student_code": "SV010",
        "student_name": "Tran Thi B",
        "email": "b.tran@gmail.com",
        "age": 22
    })
    s_id = post_res.json()["id"]

    # Chỉ sửa mỗi tuổi
    patch_res = client.patch(f"/db/students/{s_id}", json={"age": 28})
    assert patch_res.status_code == 200
    assert patch_res.json()["age"] == 28
    assert patch_res.json()["student_name"] == "Tran Thi B"  # Giữ nguyên tên cũ


# TEST 5: Kiểm tra DELETE xóa sinh viên thành công
def test_5_delete_mysql_student_success():
    post_res = client.post("/db/students", json={
        "student_code": "SV099",
        "student_name": "To Be Deleted",
        "email": "delete@gmail.com"
    })
    s_id = post_res.json()["id"]

    # Xóa sinh viên
    del_res = client.delete(f"/db/students/{s_id}")
    assert del_res.status_code == 200

    # Lấy lại sinh viên -> Trả về 404
    get_res = client.get(f"/db/students/{s_id}")
    assert get_res.status_code == 404