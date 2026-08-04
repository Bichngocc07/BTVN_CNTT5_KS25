import json
import os
from validators import is_valid_name, is_valid_email, is_valid_age

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
