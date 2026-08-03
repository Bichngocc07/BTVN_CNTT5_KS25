from fastapi import FastAPI, HTTPException, status, Depends
from typing import List
from sqlalchemy.orm import Session

from schemas import (
    StudentCreate, StudentUpdatePUT, StudentUpdatePATCH, StudentResponse,
    StudentMySQLResponse
)
import models
from database import engine, get_db

# Tạo bảng trong CSDL MySQL nếu chưa có
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Management API",
    description="API Quản lý sinh viên (Kết hợp In-Memory & MySQL SQLAlchemy)",
    version="1.0.0"
)

# CSDL Giả lập In-Memory
db_students: List[dict] = [
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
]

def find_student_index(student_id: str) -> int:
    for index, student in enumerate(db_students):
        if student["student_code"] == student_id:
            return index
    return -1


# ==========================================
# 1. API IN-MEMORY / LIST ENDPOINTS
# ==========================================

@app.get("/students", response_model=List[StudentResponse], status_code=status.HTTP_200_OK, summary="[In-Memory] Lấy danh sách tất cả sinh viên")
def get_all_students():
    return db_students

@app.get("/students/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK, summary="[In-Memory] Lấy chi tiết sinh viên theo mã")
def get_student_by_id(student_id: str):
    idx = find_student_index(student_id)
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có mã '{student_id}'"
        )
    return db_students[idx]

@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, summary="[In-Memory] Thêm sinh viên mới")
def create_student(student: StudentCreate):
    code = student.student_code.strip()
    email = str(student.email).strip()

    if find_student_index(code) != -1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã sinh viên '{code}' đã tồn tại trong hệ thống!"
        )

    if any(s["email"] == email for s in db_students):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{email}' đã tồn tại trong hệ thống!"
        )

    new_student = student.model_dump()
    new_student["student_code"] = code
    new_student["email"] = email
    db_students.append(new_student)
    return new_student

@app.put("/students/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK, summary="[In-Memory] Cập nhật PUT")
def update_student_put(student_id: str, student_data: StudentUpdatePUT):
    idx = find_student_index(student_id)
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có mã '{student_id}' để cập nhật!"
        )

    email = str(student_data.email).strip()
    for i, s in enumerate(db_students):
        if i != idx and s["email"] == email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{email}' đã được sử dụng bởi sinh viên khác!"
            )

    updated_item = {
        "student_code": student_id,
        "full_name": student_data.full_name,
        "email": email,
        "age": student_data.age,
        "is_active": student_data.is_active
    }
    db_students[idx] = updated_item
    return updated_item

@app.patch("/students/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK, summary="[In-Memory] Cập nhật PATCH")
def update_student_patch(student_id: str, student_data: StudentUpdatePATCH):
    idx = find_student_index(student_id)
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có mã '{student_id}' để cập nhật!"
        )

    current_student = db_students[idx]
    update_dict = student_data.model_dump(exclude_unset=True)

    if "email" in update_dict and update_dict["email"] is not None:
        new_email = str(update_dict["email"]).strip()
        for i, s in enumerate(db_students):
            if i != idx and s["email"] == new_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{new_email}' đã được sử dụng bởi sinh viên khác!"
                )
        update_dict["email"] = new_email

    current_student.update(update_dict)
    return current_student

@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK, summary="[In-Memory] Xóa sinh viên")
def delete_student(student_id: str):
    idx = find_student_index(student_id)
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có mã '{student_id}' để xóa!"
        )

    deleted_student = db_students.pop(idx)
    return {
        "message": f"Đã xóa thành công sinh viên '{deleted_student['full_name']}' ({student_id})",
        "student_code": student_id
    }


# ==========================================
# 2. MYSQL & SQLALCHEMY ENDPOINTS
# ==========================================

@app.get("/db/students", response_model=List[StudentMySQLResponse], status_code=status.HTTP_200_OK, summary="[MySQL] Lấy danh sách tất cả sinh viên từ DB")
def get_all_mysql_students(db: Session = Depends(get_db)):
    students = db.query(models.StudentModel).all()
    return students

@app.get("/db/students/{student_id}", response_model=StudentMySQLResponse, status_code=status.HTTP_200_OK, summary="[MySQL] Lấy chi tiết sinh viên theo ID")
def get_mysql_student_by_id(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.StudentModel).filter(models.StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có ID = {student_id} trong CSDL!"
        )
    return student
