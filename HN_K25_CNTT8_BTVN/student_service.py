import json
import math
import os
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

import models
from schemas import StudentMySQLCreate, StudentMySQLUpdate
from validators import is_valid_name, is_valid_email, is_valid_age

# --- SERVICE XỬ LÝ MYSQL DATABASE (CRUD + SEARCH / FILTER / PAGINATION) ---
class StudentDBService:
    @staticmethod
    def create_student(db: Session, student_in: StudentMySQLCreate) -> models.StudentModel:
        code = student_in.student_code.strip()
        email = str(student_in.email).strip()

        # Kiểm tra trùng Mã SV
        if db.query(models.StudentModel).filter(models.StudentModel.student_code == code).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã sinh viên '{code}' đã tồn tại trong CSDL!"
            )

        # Kiểm tra trùng Email
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

        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student

    @staticmethod
    def get_student_by_id(db: Session, student_id: int) -> models.StudentModel:
        student = db.query(models.StudentModel).filter(models.StudentModel.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy sinh viên có ID = {student_id}!"
            )
        return student

    @staticmethod
    def update_student(db: Session, student_id: int, student_in: StudentMySQLUpdate) -> models.StudentModel:
        student = StudentDBService.get_student_by_id(db, student_id)
        update_data = student_in.model_dump(exclude_unset=True)

        # Kiểm tra trùng Email nếu có cập nhật email mới
        if "email" in update_data and update_data["email"] is not None:
            new_email = str(update_data["email"]).strip()
            existing = db.query(models.StudentModel).filter(
                models.StudentModel.email == new_email,
                models.StudentModel.id != student_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{new_email}' đã được sử dụng bởi sinh viên khác!"
                )
            update_data["email"] = new_email

        for field, value in update_data.items():
            setattr(student, field, value)

        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def delete_student(db: Session, student_id: int) -> dict:
        student = StudentDBService.get_student_by_id(db, student_id)
        db.delete(student)
        db.commit()
        return {
            "message": f"Đã xóa thành công sinh viên '{student.student_name}' (ID: {student_id})"
        }

    @staticmethod
    def search_and_filter_students(
        db: Session,
        search: Optional[str] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 10
    ) -> dict:
        query = db.query(models.StudentModel)

        # 1. Tìm kiếm theo Từ khóa (Tên, Mã SV, Email)
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    models.StudentModel.student_name.ilike(search_term),
                    models.StudentModel.student_code.ilike(search_term),
                    models.StudentModel.email.ilike(search_term)
                )
            )

        # 2. Lọc theo Khoảng tuổi
        if min_age is not None:
            query = query.filter(models.StudentModel.age >= min_age)
        if max_age is not None:
            query = query.filter(models.StudentModel.age <= max_age)

        # 3. Lọc theo Trạng thái Hoạt động
        if is_active is not None:
            query = query.filter(models.StudentModel.is_active == is_active)

        # 4. Tính toán Phân trang
        total = query.count()
        total_pages = math.ceil(total / limit) if total > 0 else 1
        offset = (page - 1) * limit

        students = query.offset(offset).limit(limit).all()

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "data": students
        }


# --- SERVICE XỬ LÝ JSON CỤC BỘ / CLI (MÃ CŨ) ---
class StudentService:
    def __init__(self, storage_file="students.json"):
        self.storage_file = storage_file
        self.students = {}
        self.load_data()

    def load_data(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    self.students = json.load(f)
            except json.JSONDecodeError:
                self.students = {}

    def save_data(self):
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(self.students, f, ensure_ascii=False, indent=4)

    def generate_next_id(self) -> str:
        if not self.students:
            return "SV001"
        
        max_num = 0
        for s_id in self.students.keys():
            if s_id.startswith("SV") and s_id[2:].isdigit():
                num = int(s_id[2:])
                if num > max_num:
                    max_num = num
        
        return f"SV{max_num + 1:03d}"

    def get_existing_emails(self, ignore_id: str = None) -> set:
        return {
            s['email'] for s in self.students.values() 
            if ignore_id is None or s.get('student_id') != ignore_id
        }

    def add_student_auto_id(self, name: str, email: str, age) -> tuple[bool, str, str]:
        name = name.strip()
        email = email.strip()

        valid_name, msg_name = is_valid_name(name)
        if not valid_name: return False, msg_name, ""

        valid_email, msg_email = is_valid_email(email, self.get_existing_emails())
        if not valid_email: return False, msg_email, ""

        valid_age, msg_age, parsed_age = is_valid_age(age)
        if not valid_age: return False, msg_age, ""

        auto_id = self.generate_next_id()

        self.students[auto_id] = {
            "student_id": auto_id,
            "student_code": auto_id,
            "name": name,
            "full_name": name,
            "email": email,
            "age": parsed_age,
            "is_active": True
        }
        self.save_data()
        return True, f"Thêm thành công sinh viên: {name} với mã tự động [{auto_id}]", auto_id

    def update_student(self, student_id: str, name: str = None, email: str = None, age = None) -> tuple[bool, str]:
        student_id = student_id.strip()
        if student_id not in self.students:
            return False, f"Không tìm thấy sinh viên có mã '{student_id}'"

        student = self.students[student_id]

        if name is not None:
            name = name.strip()
            valid_name, msg_name = is_valid_name(name)
            if not valid_name: return False, msg_name
            student['name'] = name
            student['full_name'] = name

        if email is not None:
            email = email.strip()
            valid_email, msg_email = is_valid_email(email, self.get_existing_emails(ignore_id=student_id))
            if not valid_email: return False, msg_email
            student['email'] = email

        if age is not None:
            valid_age, msg_age, parsed_age = is_valid_age(age)
            if not valid_age: return False, msg_age
            student['age'] = parsed_age

        self.save_data()
        return True, f"Cập nhật thành công thông tin cho sinh viên {student_id}"

    def delete_student(self, student_id: str) -> tuple[bool, str]:
        student_id = student_id.strip()
        if student_id in self.students:
            name = self.students[student_id].get('name', '')
            del self.students[student_id]
            self.save_data()
            return True, f"Đã xóa sinh viên {name} ({student_id})"
        return False, f"Không tìm thấy sinh viên có mã '{student_id}'"

    def get_all_students(self) -> list:
        return list(self.students.values())

    def find_by_id(self, student_id: str) -> dict | None:
        return self.students.get(student_id.strip())

    def filter_by_age(self, min_age: int, max_age: int) -> list:
        return [s for s in self.students.values() if min_age <= s['age'] <= max_age]
