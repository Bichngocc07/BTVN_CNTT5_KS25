from student_service import StudentService

def print_student_table(students: list):
    if not students:
        print("  [!] Không có dữ liệu sinh viên phù hợp.")
        return
    print(f"  {'Mã SV':<10} | {'Họ và tên':<22} | {'Email':<25} | {'Tuổi':<5}")
    print("  " + "-" * 70)
    for s in students:
        print(f"  {s['student_id']:<10} | {s['name']:<22} | {s['email']:<25} | {s['age']:<5}")

def run_tests():
    print("=" * 72)
    print("CHẠY TỰ ĐỘNG BỘ KIỂM THỬ (MINIMUM 5 TEST CASES)")
    print("=" * 72)

    service = StudentService()

    # Test 1: Thêm sinh viên hợp lệ
    status1, msg1 = service.add_student("SV001", "Nguyen Van A", "a.nguyen@gmail.com", 20)
    print(f"[Test 1 - Add Valid Student]: {'PASSED' if status1 else 'FAILED'} -> {msg1}")

    # Test 2: Mã rỗng & Mã không đúng định dạng (VD thiếu tiền tố 'SV')
    status2a, msg2a = service.add_student("   ", "Tran Van B", "b.tran@gmail.com", 21)
    status2b, msg2b = service.add_student("123", "Tran Van B", "b.tran@gmail.com", 21)
    print(f"[Test 2a - Empty ID]: {'PASSED' if not status2a else 'FAILED'} -> {msg2a}")
    print(f"[Test 2b - Invalid ID Pattern]: {'PASSED' if not status2b else 'FAILED'} -> {msg2b}")

    # Test 3: Tên chỉ có khoảng trắng
    status3, msg3 = service.add_student("SV002", "   \t  ", "c.le@gmail.com", 22)
    print(f"[Test 3 - Blank Name]: {'PASSED' if not status3 else 'FAILED'} -> {msg3}")

    # Test 4: Email sai định dạng hoặc bị trùng lặp
    status4a, msg4a = service.add_student("SV003", "Le Van C", "invalid_email_format", 22)
    status4b, msg4b = service.add_student("SV004", "Pham Van D", "a.nguyen@gmail.com", 23)
    print(f"[Test 4a - Invalid Email Format]: {'PASSED' if not status4a else 'FAILED'} -> {msg4a}")
    print(f"[Test 4b - Duplicate Email]: {'PASSED' if not status4b else 'FAILED'} -> {msg4b}")

    # Test 5: Tuổi nhập chữ hoặc ngoài khoảng 17-100
    status5a, msg5a = service.add_student("SV005", "Hoang Van E", "e.hoang@gmail.com", "hai_muoi")
    status5b, msg5b = service.add_student("SV006", "Dang Van F", "f.dang@gmail.com", 15)
    print(f"[Test 5a - Non-numeric Age]: {'PASSED' if not status5a else 'FAILED'} -> {msg5a}")
    print(f"[Test 5b - Age Out of Range (<17)]: {'PASSED' if not status5b else 'FAILED'} -> {msg5b}")

    print("=" * 72 + "\n")

def main_menu():
    service = StudentService()
    # Dữ liệu khởi tạo sẵn
    service.add_student("SV001", "Nguyen Van A", "a.nguyen@gmail.com", 20)
    service.add_student("SV002", "Tran Thi B", "b.tran@gmail.com", 22)

    while True:
        print("\n=== HỆ THỐNG QUẢN LÝ SINH VIÊN ===")
        print("1. Thêm sinh viên mới")
        print("2. Hiển thị danh sách sinh viên")
        print("3. Tìm sinh viên theo mã")
        print("4. Lọc sinh viên theo khoảng tuổi")
        print("0. Thoát")
        
        choice = input("Lựa chọn của bạn (0-4): ").strip()

        if choice == "1":
            s_id = input("Mã SV (VD: SV001): ")
            name = input("Họ tên: ")
            email = input("Email: ")
            age = input("Tuổi: ")
            _, msg = service.add_student(s_id, name, email, age)
            print(f"[=>] {msg}")

        elif choice == "2":
            print_student_table(service.get_all_students())

        elif choice == "3":
            s_id = input("Nhập mã SV cần tìm: ")
            student = service.find_by_id(s_id)
            print_student_table([student] if student else [])

        elif choice == "4":
            try:
                min_a = int(input("Tuổi tối thiểu: "))
                max_a = int(input("Tuổi tối đa: "))
                print_student_table(service.filter_by_age(min_a, max_a))
            except ValueError:
                print("[!] Vui lòng nhập số nguyên hợp lệ!")

        elif choice == "0":
            print("Đã thoát chương trình.")
            break

if __name__ == "__main__":
    run_tests()
    main_menu()
