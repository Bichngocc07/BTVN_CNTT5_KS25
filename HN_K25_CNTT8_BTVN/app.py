@app.put(
    "/db/students/{student_id}", 
    response_model=StudentMySQLResponse, 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Cập nhật toàn bộ thông tin sinh viên (PUT)"
)
def update_mysql_student(
    student_id: int, 
    student_in: StudentUpdatePUT, 
    db: Session = Depends(get_db)
):
    return StudentDBService.update_student(db, student_id, student_in)


@app.patch(
    "/db/students/{student_id}", 
    response_model=StudentMySQLResponse, 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Cập nhật một phần thông tin sinh viên (PATCH)"
)
def patch_mysql_student(
    student_id: int, 
    student_data: StudentUpdatePATCH, 
    db: Session = Depends(get_db)
):
    update_dict = student_data.model_dump(exclude_unset=True)
    return StudentDBService.patch_student(db, student_id, update_dict)


@app.delete(
    "/db/students/{student_id}", 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Xóa sinh viên theo ID"
)
def delete_mysql_student(
    student_id: int, 
    db: Session = Depends(get_db)
):
    return StudentDBService.delete_student(db, student_id)


@app.get(
    "/db/students/search", 
    response_model=List[StudentMySQLResponse], 
    status_code=status.HTTP_200_OK, 
    summary="[MySQL] Tìm kiếm và lọc danh sách sinh viên theo từ khóa/tuổi"
)
def search_mysql_students(
    keyword: str = None, 
    min_age: int = None, 
    max_age: int = None, 
    db: Session = Depends(get_db)
):
    return StudentDBService.search_students(db, keyword=keyword, min_age=min_age, max_age=max_age)
