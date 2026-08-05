from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional

# Schema Request POST
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
            raise ValueError('Không được để rỗng!')
        return v


# Schema Request PUT (Cập nhật toàn bộ)
class StudentMySQLUpdatePUT(BaseModel):
    student_code: str = Field(..., description="Mã sinh viên")
    student_name: str = Field(..., description="Họ và tên")
    email: EmailStr = Field(..., description="Email hợp lệ")
    age: Optional[int] = Field(None, ge=18, le=60)
    phone_number: Optional[str] = Field(None)
    is_active: bool = Field(True)

    @field_validator('student_code', 'student_name')
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Không được để rỗng!')
        return v


# Schema Request PATCH (Cập nhật một phần)
class StudentMySQLUpdatePATCH(BaseModel):
    student_code: Optional[str] = Field(None)
    student_name: Optional[str] = Field(None)
    email: Optional[EmailStr] = Field(None)
    age: Optional[int] = Field(None, ge=18, le=60)
    phone_number: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)


# Schema Response
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
