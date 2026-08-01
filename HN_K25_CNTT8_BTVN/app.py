from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List, Optional

app = FastAPI(
    title="Student Management API",
    description="API Quản lý sinh viên CRUD lưu trong danh sách (List in-memory)",
    version="1.0.0"
)

# Cơ sở dữ liệu giả lập sử dụng List
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

# --- SCHEMAS ---

class StudentCreate(BaseModel):
    student_code: str = Field(..., description="Mã sinh viên")
    full_name: str = Field(..., description="Họ và tên")
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


class StudentUpdatePUT(BaseModel):
    """Schema cập nhật toàn bộ thông tin (PUT) - Trừ student_code"""
    full_name: str = Field(..., description="Họ và tên")
    email: EmailStr = Field(..., description="Email hợp lệ")
    age: int = Field(..., ge=18, le=60, description="Tuổi từ 18 đến 60")
    is_active: bool = Field(default=True, description="Trạng thái")

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Tên sinh viên không được để rỗng hoặc chỉ chứa khoảng trắng')
        return v


class StudentUpdatePATCH(BaseModel):
    """Schema cập nhật một phần thông tin (PATCH)"""
    full_name: Optional[str] = Field(None, description="Họ và tên")
    email: Optional[EmailStr] = Field(None, description="Email hợp lệ")
    age: Optional[int] = Field(None, ge=18, le=60, description="Tuổi từ 18 đến 60")
    is_active: Optional[bool] = Field(None, description="Trạng thái")

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Tên sinh viên không được để rỗng')
        return v


class StudentResponse(StudentCreate):
    pass


# --- HELPER FUNCTIONS ---

def find_student_index(student_id: str) -> int:
    """Tìm chỉ số của sinh viên trong list dựa vào mã sinh viên"""
    for index, student in enumerate(db_students):
        if student["student_code"] == student_id:
            return index
    return -1


# --- API ENDPOINTS ---

@app.get("/students", response_model=List[StudentResponse], status_code=status.HTTP_200_OK, summary="Lấy danh sách tất cả sinh viên")
def get_all_students():
    return db_students


@app.get("/students/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK, summary="Lấy chi tiết sinh viên theo mã")
def get_student_by_id(student_id: str):
    idx = find_student_index(student_id)
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có mã '{student_id}'"
        )
    return db_students[idx]


@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, summary="Thêm sinh viên mới")
def create_student(student: StudentCreate):
    code = student.student_code.strip()
    email = str(student.email).strip()

    # Kiểm tra trùng Mã SV
    if find_student_index(code) != -1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã sinh viên '{code}' đã tồn tại trong hệ thống!"
        )

    # Kiểm tra trùng Email
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


@app.put("/students/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK, summary="Cập nhật toàn bộ thông tin sinh viên (PUT)")
def update_student_put(student_id: str, student_data: StudentUpdatePUT):
    idx = find_student_index(student_id)
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có mã '{student_id}' để cập nhật!"
        )

    email = str(student_data.email).strip()

    # Chặn trùng email với các sinh viên khác
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


@app.patch("/students/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK, summary="Cập nhật một phần thông tin sinh viên (PATCH)")
def update_student_patch(student_id: str, student_data: StudentUpdatePATCH):
    idx = find_student_index(student_id)
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có mã '{student_id}' để cập nhật!"
        )

    current_student = db_students[idx]
    update_dict = student_data.model_dump(exclude_unset=True)

    # Nếu có cập nhật email, kiểm tra xem email mới có trùng không
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


@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK, summary="Xóa sinh viên")
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
