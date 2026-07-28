from validators import is_valid_student_id, is_valid_name, is_valid_email, is_valid_age

class StudentService:
    def __init__(self):
        # Lưu trữ dưới dạng Dictionary để tối ưu tốc độ tìm kiếm theo Mã sinh viên
        # Key: student_id, Value: dict thông tin sinh viên
        self.students = {}

    def get_existing_emails(self) -> set:
        return {student['email'] for student in self.students.values()}

    def add_student(self, student_id: str, name: str, email: str, age) -> tuple[bool, str]:
        """Thêm sinh viên mới sau khi qua các bước validation."""
        student_id = student_id.strip()
        name = name.strip()
        email = email.strip()

        # Validate ID
        valid_id, msg_id = is_valid_student_id(student_id, set(self.students.keys()))
        if not valid_id:
            return False, msg_id

        # Validate Name
        valid_name, msg_name = is_valid_name(name)
        if not valid_name:
            return False, msg_name

        # Validate Email
        valid_email, msg_email = is_valid_email(email, self.get_existing_emails())
        if not valid_email:
            return False, msg_email

        # Validate Age
        valid_age, msg_age, parsed_age = is_valid_age(age)
        if not valid_age:
            return False, msg_age

        # Thêm vào cơ sở dữ liệu
        self.students[student_id] = {
            "student_id": student_id,
            "name": name,
            "email": email,
            "age": parsed_age
        }
        return True, f"Thêm thành công sinh viên: {name} ({student_id})"

    def get_all_students(self) -> list:
        """Lấy toàn bộ danh sách sinh viên."""
        return list(self.students.values())

    def find_by_id(self, student_id: str) -> dict | None:
        """Tìm kiếm sinh viên theo mã."""
        return self.students.get(student_id.strip())

    def filter_by_age(self, min_age: int, max_age: int) -> list:
        """Lọc danh sách sinh viên theo khoảng tuổi."""
        result = []
        for student in self.students.values():
            if min_age <= student['age'] <= max_age:
                result.append(student)
        return result