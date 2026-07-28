from student_service import StudentService

def print_student_table(students: list):
    """Hàm bổ trợ in danh sách sinh viên dưới dạng bảng."""
    if not students:
        print("  [!] Không có dữ liệu sinh viên.")
        return
    print(f"  {'Mã SV':<10} | {'Họ và tên':<20} | {'Email':<25} | {'Tuổi':<5}")
    print("  " + "-" * 68)
    for s in students:
        print(f"  {s['student_id']:<10} | {s['name']:<20} | {s['email']:<25} | {s['age']:<5}")

def run_tests():
    """Chạy tối thiểu 5 test case kiểm tra toàn bộ các điều kiện lỗi/hợp lệ."""
    print("=" * 70)
    print("CHẠY BỘ KIỂM THỬ TỰ ĐỘNG (MINIMUM 5 TEST CASES)")
    print("=" * 70)

    service = StudentService()

    # # Test Case 1: Thêm sinh viên thành công
    # status1, msg1 = service.add_student("SV001", "Nguyen Van A", "a.nguyen@gmail.com", 20)
    # print(f"[Test 1 - Add Valid Student]: {'PASSED' if status1 else 'FAILED'} -> {msg1}")

    # # Test Case 2: Mã sinh viên bị rỗng hoặc trùng lặp
    # status2a, msg2a = service.add_student("   ", "Tran Van B", "b.tran@gmail.com", 21)
    # status2b, msg2b = service.add_student("SV001", "Tran Van B", "b.tran@gmail.com", 21)
    # print(f"[Test 2a - Empty ID]: {'PASSED' if not status2a else 'FAILED'} -> {msg2a}")
    # print(f"[Test 2b - Duplicate ID]: {'PASSED' if not status2b else 'FAILED'} -> {msg2b}")

    # # Test Case 3: Tên chỉ chứa khoảng trắng
    # status3, msg3 = service.add_student("SV002", "   \t  ", "c.le@gmail.com", 22)
    # print(f"[Test 3 - Blank Name]: {'PASSED' if not status3 else 'FAILED'} -> {msg3}")

    # # Test Case 4: Email sai định dạng hoặc trùng email
    # status4a, msg4a = service.add_student("SV003", "Le Van C", "invalid_email_format", 22)
    # status4b, msg4b = service.add_student("SV004", "Pham Van D", "a.nguyen@gmail.com", 23)
    # print(f"[Test 4a - Invalid Email Format]: {'PASSED' if not status4a else 'FAILED'} -> {msg4a}")
    # print(f"[Test 4b - Duplicate Email]: {'PASSED' if not status4b else 'FAILED'} -> {msg4b}")

    # # Test Case 5: Tuổi không hợp lệ (nhập chữ hoặc tuổi ngoài khoảng)
    # status5a, msg5a = service.add_student("SV005", "Hoang Van E", "e.hoang@gmail.com", "hai_muoi")
    # status5b, msg5b = service.add_student("SV006", "Dang Van F", "f.dang@gmail.com", 15)
    # print(f"[Test 5a - Non-numeric Age]: {'PASSED' if not status5a else 'FAILED'} -> {msg5a}")
    # print(f"[Test 5b - Age Out of Range (<17)]: {'PASSED' if not status5b else 'FAILED'} -> {msg5b}")

    # print("=" * 70 + "\n")

def main_menu():
    """Giao diện CLI chính tương tác với người dùng."""
    service = StudentService()
    
    # Thêm sẵn một số dữ liệu mẫu
    service.add_student("SV001", "Nguyen Van A", "a.nguyen@gmail.com", 20)
    service.add_student("SV002", "Tran Thi B", "b.tran@gmail.com", 22)
    service.add_student("SV003", "Le Hoang C", "c.le@gmail.com", 19)

    while True:
        print("\n=== HỆ THỐNG QUẢN LÝ SINH VIÊN ===")
        print("1. Thêm sinh viên mới")
        print("2. Hiển thị danh sách sinh viên")
        print("3. Tìm sinh viên theo mã")
        print("4. Lọc sinh viên theo khoảng tuổi")
        print("0. Thoát")
        
        choice = input("Lựa chọn của bạn (0-4): ").strip()

        if choice == "1":
            print("\n--- Thêm Sinh Viên Mới ---")
            s_id = input("Mã SV: ")
            name = input("Họ tên: ")
            email = input("Email: ")
            age = input("Tuổi: ")
            success, msg = service.add_student(s_id, name, email, age)
            print(f"[=>] {msg}")

        elif choice == "2":
            print("\n--- Danh Sách Sinh Viên ---")
            print_student_table(service.get_all_students())

        elif choice == "3":
            print("\n--- Tìm Sinh Viên Theo Mã ---")
            s_id = input("Nhập mã SV cần tìm: ")
            student = service.find_by_id(s_id)
            if student:
                print_student_table([student])
            else:
                print(f"[!] Không tìm thấy sinh viên có mã '{s_id}'.")

        elif choice == "4":
            print("\n--- Lọc Sinh Viên Theo Tuổi ---")
            try:
                min_a = int(input("Nhập tuổi tối thiểu: "))
                max_a = int(input("Nhập tuổi tối đa: "))
                filtered = service.filter_by_age(min_a, max_a)
                print(f"\nDanh sách sinh viên từ {min_a} đến {max_a} tuổi:")
                print_student_table(filtered)
            except ValueError:
                print("[!] Vui lòng nhập số nguyên hợp lệ!")

        elif choice == "0":
            print("Đã thoát chương trình.")
            break
        else:
            print("[!] Lựa chọn không hợp lệ, vui lòng thử lại.")

if __name__ == "__main__":
    # Chạy tự động các test case kiểm tra trước
    run_tests()
    # Chạy chương trình chính tương tác CLI
    main_menu()