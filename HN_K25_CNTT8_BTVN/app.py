from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List
from student_service import StudentService

app = FastAPI(
    title="Student Management API",
    description="API Quản lý sinh viên sử dụng Pydantic Model & Validation",
    version="1.0.0"
)

service = StudentService("students.json")

# Pydantic Request Schema
class StudentCreate(BaseModel):
    student_code: str = Field(..., description="Mã sinh viên, không được rỗng")
    full_name: str = Field(..., description="Tên sinh viên, không được chỉ chứa khoảng trắng")
    email: EmailStr = Field(..., description="Email hợp lệ")
    age: int = Field(..., ge=18, le=60, description="Tuổi từ 18 đến 60")
    is_active: bool = Field(default=True, description="Trạng thái hoạt động")

    @field_validator('student_code')
    @classmethod
    def validate_student_code(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Mã sinh viên không được để rỗng hoặc chỉ chứa khoảng trắng')
        return v

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Tên sinh viên không được để rỗng hoặc chỉ chứa khoảng trắng')
        return v

class StudentResponse(StudentCreate):
    pass

@app.get("/students", response_model=List[dict], summary="Lấy danh sách sinh viên")
def get_students():
    return service.get_all_students()

@app.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm sinh viên mới (Request Body Validation)"
)
def create_student(student: StudentCreate):
    code = student.student_code.strip()
    email = str(student.email).strip()

    # Chặn trùng mã sinh viên
    if service.find_by_id(code) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã sinh viên '{code}' đã tồn tại trong hệ thống!"
        )

    # Chặn trùng email
    if email in service.get_existing_emails():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{email}' đã tồn tại trong hệ thống!"
        )

    # Lưu sinh viên mới
    service.students[code] = {
        "student_id": code,
        "student_code": code,
        "name": student.full_name,
        "full_name": student.full_name,
        "email": email,
        "age": student.age,
        "is_active": student.is_active
    }
    service.save_data()
    return student