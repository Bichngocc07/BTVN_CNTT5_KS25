from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List

# --- SCHEMAS MYSQL (CREATE / UPDATE / RESPONSE) ---
class StudentMySQLCreate(BaseModel):
    student_code: str = Field(..., description="Mã sinh viên (VD: SV001)")
    student_name: str = Field(..., description="Họ và tên")
    email: EmailStr = Field(..., description="Email hợp lệ")
    age: Optional[int] = Field(None, ge=18, le=60, description="Tuổi từ 18 đến 60")
    phone_number: Optional[str] = Field(None, description="Số điện thoại")
    password: Optional[str] = Field("123456", description="Mật khẩu")

    @field_validator('student_code', 'student_name')
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Trường này không được để rỗng hoặc chỉ chứa khoảng trắng')
        return v

class StudentMySQLUpdate(BaseModel):
    student_name: Optional[str] = Field(None, description="Họ và tên")
    email: Optional[EmailStr] = Field(None, description="Email hợp lệ")
    age: Optional[int] = Field(None, ge=18, le=60, description="Tuổi từ 18 đến 60")
    phone_number: Optional[str] = Field(None, description="Số điện thoại")
    is_active: Optional[bool] = Field(None, description="Trạng thái hoạt động")

    @field_validator('student_name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Tên không được để rỗng')
        return v

class StudentMySQLResponse(BaseModel):
    id: int
    student_code: str
    student_name: str
    email: EmailStr
    age: Optional[int] = None
    phone_number: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

# Schema trả về kết quả Search/Filter kèm Phân trang
class PaginatedStudentResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    data: List[StudentMySQLResponse]

# --- SCHEMAS IN-MEMORY (CŨ) ---
class StudentCreate(BaseModel):
    student_code: str = Field(..., description="Mã sinh viên")
    full_name: str = Field(..., description="Họ và tên")
    email: EmailStr = Field(..., description="Email hợp lệ")
    age: int = Field(..., ge=18, le=60, description="Tuổi từ 18 đến 60")
    is_active: bool = Field(default=True, description="Trạng thái hoạt động")

    @field_validator('student_code', 'full_name')
    @classmethod
    def validate_str_fields(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Không được để rỗng')
        return v

class StudentUpdatePUT(BaseModel):
    full_name: str = Field(..., description="Họ và tên")
    email: EmailStr = Field(..., description="Email hợp lệ")
    age: int = Field(..., ge=18, le=60, description="Tuổi từ 18 đến 60")
    is_active: bool = Field(default=True, description="Trạng thái")

class StudentUpdatePATCH(BaseModel):
    full_name: Optional[str] = Field(None, description="Họ và tên")
    email: Optional[EmailStr] = Field(None, description="Email hợp lệ")
    age: Optional[int] = Field(None, ge=18, le=60, description="Tuổi từ 18 đến 60")
    is_active: Optional[bool] = Field(None, description="Trạng thái")

class StudentResponse(StudentCreate):
    pass
