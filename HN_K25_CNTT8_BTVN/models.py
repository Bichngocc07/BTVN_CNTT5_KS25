from sqlalchemy import Column, Integer, String
from database import Base

class StudentModel(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Mật khẩu
    phone_number = Column(String(20), nullable=True)