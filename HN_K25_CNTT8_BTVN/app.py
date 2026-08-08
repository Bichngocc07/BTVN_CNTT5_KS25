from fastapi import FastAPI, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session

import models
from database import engine, get_db
from schemas import (
    StudentMySQLCreate, StudentMySQLUpdate, StudentMySQLResponse, PaginatedStudentResponse,
    StudentCreate, StudentUpdatePUT, StudentUpdatePATCH, StudentResponse
)
from student_service import StudentDBService

# Tạo bảng tự động trong MySQL nếu chưa tồn tại
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Management API",
    description="API Quản lý sinh viên: CRUD MySQL, Validation & Search/Filter/Pagination",
    version="2.0.0"
)

# ==========================================================
# 1. CÁC API CSDL MYSQL (CRUD + SEARCH / FILTER / PAGINATION)
# ==========================================================

@app.post(
    "/db/students", 
    response_model=StudentMySQLResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="[MySQL] Thêm mới sinh viên (Create)"
)
def create_mysql_student(
    student_in: StudentMySQLCreate, 
    db: Session = Depends(get_db)
):
    return StudentDBService.create_student(db, student_in)


@app.get(
    "/db/students", 
    response_model=PaginatedStudentResponse, 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Lấy danh sách, Tìm kiếm, Lọc & Phân trang (Search & Filter & Read All)"
)
def search_and_filter_mysql_students(
    search: Optional[str] = Query(None, description="Tìm kiếm theo Tên, Mã SV hoặc Email"),
    min_age: Optional[int] = Query(None, ge=18, le=60, description="Lọc tuổi tối thiểu"),
    max_age: Optional[int] = Query(None, ge=18, le=60, description="Lọc tuổi tối đa"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động"),
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    limit: int = Query(10, ge=1, le=100, description="Số lượng kết quả trên mỗi trang"),
    db: Session = Depends(get_db)
):
    return StudentDBService.search_and_filter_students(
        db=db,
        search=search,
        min_age=min_age,
        max_age=max_age,
        is_active=is_active,
        page=page,
        limit=limit
    )


@app.get(
    "/db/students/{student_id}", 
    response_model=StudentMySQLResponse, 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Xem chi tiết sinh viên theo ID (Read One)"
)
def get_mysql_student_by_id(
    student_id: int, 
    db: Session = Depends(get_db)
):
    return StudentDBService.get_student_by_id(db, student_id)


@app.patch(
    "/db/students/{student_id}", 
    response_model=StudentMySQLResponse, 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Cập nhật thông tin sinh viên (Update)"
)
def update_mysql_student(
    student_id: int, 
    student_in: StudentMySQLUpdate, 
    db: Session = Depends(get_db)
):
    return StudentDBService.update_student(db, student_id, student_in)


@app.delete(
    "/db/students/{student_id}", 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Xóa sinh viên theo ID (Delete)"
)
def delete_mysql_student(
    student_id: int, 
    db: Session = Depends(get_db)
):
    return StudentDBService.delete_student(db, student_id)


# ==========================================================
# 2. CÁC API IN-MEMORY / LIST DỮ LIỆU GIẢ LẬP (MÃ CŨ)
# ==========================================================

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

@app.get("/students", response_model=List[StudentResponse], status_code=status.HTTP_200_OK)
def get_all_students():
    return db_students

@app.get("/students/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
def get_student_by_id(student_id: str):
    idx = find_student_index(student_id)
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có mã '{student_id}'"
        )
    return db_students[idx]

@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate):
    code = student.student_code.strip()
    email = str(student.email).strip()

    if find_student_index(code) != -1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã sinh viên '{code}' đã tồn tại!"
        )

    if any(s["email"] == email for s in db_students):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{email}' đã tồn tại!"
        )

    new_student = student.model_dump()
    new_student["student_code"] = code
    new_student["email"] = email
    db_students.append(new_student)
    return new_student

@app.put("/students/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
def update_student_put(student_id: str, student_data: StudentUpdatePUT):
    idx = find_student_index(student_id)
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có mã '{student_id}'"
        )

    email = str(student_data.email).strip()
    for i, s in enumerate(db_students):
        if i != idx and s["email"] == email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{email}' đã được sử dụng!"
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

@app.patch("/students/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
def update_student_patch(student_id: str, student_data: StudentUpdatePATCH):
    idx = find_student_index(student_id)
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có mã '{student_id}'"
        )

    current_student = db_students[idx]
    update_dict = student_data.model_dump(exclude_unset=True)

    if "email" in update_dict and update_dict["email"] is not None:
        new_email = str(update_dict["email"]).strip()
        for i, s in enumerate(db_students):
            if i != idx and s["email"] == new_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{new_email}' đã được sử dụng!"
                )
        update_dict["email"] = new_email

    current_student.update(update_dict)
    return current_student

@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(student_id: str):
    idx = find_student_index(student_id)
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có mã '{student_id}'"
        )

    deleted_student = db_students.pop(idx)
    return {
        "message": f"Đã xóa thành công sinh viên '{deleted_student['full_name']}' ({student_id})",
        "student_code": student_id
    }
