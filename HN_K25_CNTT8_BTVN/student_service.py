from validators import is_valid_student_id, is_valid_name, is_valid_email, is_valid_age

class StudentService:
    def __init__(self):
        # Sử dụng Dictionary với Key là student_id để tối ưu tốc độ tìm kiếm O(1)
        self.students = {}

    def get_existing_emails(self) -> set:
        return {student['email'] for student in self.students.values()}

    def add_student(self, student_id: str, name: str, email: str, age) -> tuple[bool, str]:
        student_id = student_id.strip()
        name = name.strip()
        email = email.strip()

        # Validate từng thuộc tính
        valid_id, msg_id = is_valid_student_id(student_id, set(self.students.keys()))
        if not valid_id:
            return False, msg_id

        valid_name, msg_name = is_valid_name(name)
        if not valid_name:
            return False, msg_name

        valid_email, msg_email = is_valid_email(email, self.get_existing_emails())
        if not valid_email:
            return False, msg_email

        valid_age, msg_age, parsed_age = is_valid_age(age)
        if not valid_age:
            return False, msg_age

        # Thêm vào dictionary lưu trữ
        self.students[student_id] = {
            "student_id": student_id,
            "name": name,
            "email": email,
            "age": parsed_age
        }
        return True, f"Thêm thành công sinh viên: {name} ({student_id})"

    def get_all_students(self) -> list:
        return list(self.students.values())

    def find_by_id(self, student_id: str) -> dict | None:
        return self.students.get(student_id.strip())

    def filter_by_age(self, min_age: int, max_age: int) -> list:
        return [s for s in self.students.values() if min_age <= s['age'] <= max_age]
