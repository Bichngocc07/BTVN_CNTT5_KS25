from fastapi import FastAPI, HTTPException, status, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import models
from database import engine, get_db
from schemas import (
    StudentMySQLCreate, 
    StudentMySQLResponse, 
    StudentMySQLUpdatePUT, 
    StudentMySQLUpdatePATCH
)

# Tự động tạo bảng trong CSDL MySQL nếu chưa có
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Management API",
    description="API Quản lý sinh viên kết nối CSDL MySQL qua SQLAlchemy (Full CRUD)",
    version="1.0.0"
)

# ==========================================================
# CÁC API THAO TÁC CSDL MYSQL (CREATE, READ, UPDATE, DELETE)
# ==========================================================

# 1. POST /db/students - Thêm mới sinh viên
@app.post(
    "/db/students", 
    response_model=StudentMySQLResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="[MySQL] Thêm sinh viên mới"
)
def create_mysql_student(student_in: StudentMySQLCreate, db: Session = Depends(get_db)):
    code = student_in.student_code.strip()
    email = str(student_in.email).strip()

    # Chặn trùng Mã sinh viên
    if db.query(models.StudentModel).filter(models.StudentModel.student_code == code).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã sinh viên '{code}' đã tồn tại trong CSDL!"
        )

    # Chặn trùng Email
    if db.query(models.StudentModel).filter(models.StudentModel.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{email}' đã tồn tại trong CSDL!"
        )

    new_student = models.StudentModel(
        student_code=code,
        student_name=student_in.student_name.strip(),
        email=email,
        password=student_in.password,
        phone_number=student_in.phone_number,
        age=student_in.age,
        is_active=True
    )

    try:
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi thao tác CSDL: {str(e)}"
        )


# 2. GET /db/students - Lấy tất cả sinh viên
@app.get(
    "/db/students", 
    response_model=List[StudentMySQLResponse], 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Lấy danh sách tất cả sinh viên"
)
def get_all_mysql_students(db: Session = Depends(get_db)):
    return db.query(models.StudentModel).all()


# 3. GET /db/students/{student_id} - Lấy chi tiết sinh viên theo ID
@app.get(
    "/db/students/{student_id}", 
    response_model=StudentMySQLResponse, 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Lấy chi tiết sinh viên theo ID"
)
def get_mysql_student_by_id(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.StudentModel).filter(models.StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có ID = {student_id} trong CSDL!"
        )
    return student


# 4. PUT /db/students/{student_id} - Cập nhật toàn bộ thông tin sinh viên
@app.put(
    "/db/students/{student_id}", 
    response_model=StudentMySQLResponse, 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Cập nhật toàn bộ thông tin sinh viên (PUT)"
)
def update_mysql_student_put(
    student_id: int, 
    student_in: StudentMySQLUpdatePUT, 
    db: Session = Depends(get_db)
):
    student = db.query(models.StudentModel).filter(models.StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có ID = {student_id} để cập nhật!"
        )

    new_code = student_in.student_code.strip()
    new_email = str(student_in.email).strip()

    # Chặn trùng Mã sinh viên với bản ghi khác
    dup_code = db.query(models.StudentModel).filter(
        models.StudentModel.student_code == new_code,
        models.StudentModel.id != student_id
    ).first()
    if dup_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã sinh viên '{new_code}' đã được sử dụng bởi sinh viên khác!"
        )

    # Chặn trùng Email với bản ghi khác
    dup_email = db.query(models.StudentModel).filter(
        models.StudentModel.email == new_email,
        models.StudentModel.id != student_id
    ).first()
    if dup_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{new_email}' đã được sử dụng bởi sinh viên khác!"
        )

    student.student_code = new_code
    student.student_name = student_in.student_name.strip()
    student.email = new_email
    student.age = student_in.age
    student.phone_number = student_in.phone_number
    student.is_active = student_in.is_active

    try:
        db.commit()
        db.refresh(student)
        return student
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cập nhật CSDL: {str(e)}"
        )


# 5. PATCH /db/students/{student_id} - Cập nhật một phần thông tin sinh viên
@app.patch(
    "/db/students/{student_id}", 
    response_model=StudentMySQLResponse, 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Cập nhật một phần thông tin sinh viên (PATCH)"
)
def update_mysql_student_patch(
    student_id: int, 
    student_in: StudentMySQLUpdatePATCH, 
    db: Session = Depends(get_db)
):
    student = db.query(models.StudentModel).filter(models.StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có ID = {student_id} để cập nhật!"
        )

    update_data = student_in.model_dump(exclude_unset=True)

    # Kiểm tra chặn trùng Mã sinh viên nếu có truyền student_code
    if "student_code" in update_data and update_data["student_code"] is not None:
        new_code = update_data["student_code"].strip()
        dup_code = db.query(models.StudentModel).filter(
            models.StudentModel.student_code == new_code,
            models.StudentModel.id != student_id
        ).first()
        if dup_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã sinh viên '{new_code}' đã tồn tại!"
            )
        update_data["student_code"] = new_code

    # Kiểm tra chặn trùng Email nếu có truyền email
    if "email" in update_data and update_data["email"] is not None:
        new_email = str(update_data["email"]).strip()
        dup_email = db.query(models.StudentModel).filter(
            models.StudentModel.email == new_email,
            models.StudentModel.id != student_id
        ).first()
        if dup_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{new_email}' đã tồn tại!"
            )
        update_data["email"] = new_email

    for key, value in update_data.items():
        setattr(student, key, value)

    try:
        db.commit()
        db.refresh(student)
        return student
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cập nhật CSDL: {str(e)}"
        )


# 6. DELETE /db/students/{student_id} - Xóa sinh viên
@app.delete(
    "/db/students/{student_id}", 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Xóa sinh viên khỏi CSDL"
)
def delete_mysql_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.StudentModel).filter(models.StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có ID = {student_id} để xóa!"
        )

    try:
        db.delete(student)
        db.commit()
        return {
            "message": f"Đã xóa thành công sinh viên '{student.student_name}' (ID: {student_id}) khỏi CSDL!",
            "id": student_id
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa dữ liệu từ CSDL: {str(e)}"
        )
