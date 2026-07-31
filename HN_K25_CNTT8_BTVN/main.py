from student_service import StudentService

def print_student_table(students: list):
    if not students:
        print("  [!] Không có dữ liệu sinh viên phù hợp.")
        return
    print(f"  {'Mã SV':<10} | {'Họ và tên':<22} | {'Email':<25} | {'Tuổi':<5}")
    print("  " + "-" * 70)
    for s in students:
        name = s.get('full_name') or s.get('name')
        s_id = s.get('student_code') or s.get('student_id')
        print(f"  {s_id:<10} | {name:<22} | {s['email']:<25} | {s['age']:<5}")

def main_menu():
    service = StudentService("students.json")
    
    # Khởi tạo dữ liệu mẫu nếu file đang trống
    if not service.get_all_students():
        service.add_student_auto_id("Nguyen Van A", "a.nguyen@gmail.com", 20)
        service.add_student_auto_id("Tran Thi B", "b.tran@gmail.com", 22)

    while True:
        print("\n=== HỆ THỐNG QUẢN LÝ SINH VIÊN (TỰ ĐỘNG SINH MÃ) ===")
        print("1. Thêm sinh viên mới (Tự động cấp mã)")
        print("2. Hiển thị danh sách sinh viên")
        print("3. Tìm sinh viên theo mã")
        print("4. Lọc sinh viên theo khoảng tuổi")
        print("5. Sửa thông tin sinh viên")
        print("6. Xóa sinh viên")
        print("0. Thoát")
        
        choice = input("Lựa chọn của bạn (0-6): ").strip()

        if choice == "1":
            print("\n--- Thêm Sinh Viên Mới ---")
            name = input("Họ tên: ")
            email = input("Email: ")
            age = input("Tuổi: ")
            
            success, msg, generated_id = service.add_student_auto_id(name, email, age)
            print(f"[=>] {msg}")

        elif choice == "2":
            print("\n--- Danh Sách Sinh Viên ---")
            print_student_table(service.get_all_students())

        elif choice == "3":
            s_id = input("Nhập mã SV cần tìm (VD: SV001): ")
            student = service.find_by_id(s_id)
            print_student_table([student] if student else [])

        elif choice == "4":
            try:
                min_a = int(input("Tuổi tối thiểu: "))
                max_a = int(input("Tuổi tối đa: "))
                print_student_table(service.filter_by_age(min_a, max_a))
            except ValueError:
                print("[!] Vui lòng nhập số nguyên hợp lệ!")

        elif choice == "5":
            s_id = input("Nhập mã SV cần sửa: ")
            student = service.find_by_id(s_id)
            if not student:
                print(f"[!] Không tìm thấy sinh viên có mã '{s_id}'")
            else:
                curr_name = student.get('full_name') or student.get('name')
                print(f"--- Đang sửa sinh viên {s_id} (Nhấn Enter để giữ nguyên) ---")
                new_name = input(f"Họ tên mới [{curr_name}]: ").strip()
                new_email = input(f"Email mới [{student['email']}]: ").strip()
                new_age = input(f"Tuổi mới [{student['age']}]: ").strip()

                _, msg = service.update_student(
                    student_id=s_id,
                    name=new_name if new_name else None,
                    email=new_email if new_email else None,
                    age=new_age if new_age else None
                )
                print(f"[=>] {msg}")

        elif choice == "6":
            s_id = input("Nhập mã SV cần xóa: ")
            confirm = input(f"Bạn có chắc muốn xóa sinh viên '{s_id}'? (y/n): ").strip().lower()
            if confirm == 'y':
                _, msg = service.delete_student(s_id)
                print(f"[=>] {msg}")

        elif choice == "0":
            print("Đã lưu dữ liệu và thoát chương trình.")
            break

if __name__ == "__main__":
    main_menu()
