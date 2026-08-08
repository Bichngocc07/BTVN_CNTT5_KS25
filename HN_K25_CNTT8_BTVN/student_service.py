@staticmethod
    def update_student(db: Session, student_id: int, student_in: StudentUpdatePUT) -> models.StudentModel:
        student = db.query(models.StudentModel).filter(models.StudentModel.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy sinh viên có ID = {student_id} trong CSDL!"
            )
        
        email = str(student_in.email).strip()

        # Kiểm tra trùng email với sinh viên khác
        existing_email = db.query(models.StudentModel).filter(
            models.StudentModel.email == email, 
            models.StudentModel.id != student_id
        ).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email '{email}' đã được sử dụng!")

        student.student_name = student_in.full_name.strip()
        student.email = email
        student.age = student_in.age
        student.is_active = student_in.is_active

        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def patch_student(db: Session, student_id: int, update_data: dict) -> models.StudentModel:
        student = db.query(models.StudentModel).filter(models.StudentModel.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy sinh viên có ID = {student_id} trong CSDL!"
            )

        if "email" in update_data and update_data["email"] is not None:
            new_email = str(update_data["email"]).strip()
            existing_email = db.query(models.StudentModel).filter(
                models.StudentModel.email == new_email, 
                models.StudentModel.id != student_id
            ).first()
            if existing_email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email '{new_email}' đã được sử dụng!")
            update_data["email"] = new_email

        if "full_name" in update_data and update_data["full_name"] is not None:
            update_data["student_name"] = update_data.pop("full_name").strip()

        for key, value in update_data.items():
            if value is not None:
                setattr(student, key, value)

        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def delete_student(db: Session, student_id: int):
        student = db.query(models.StudentModel).filter(models.StudentModel.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy sinh viên có ID = {student_id} trong CSDL!"
            )
        db.delete(student)
        db.commit()
        return {"message": f"Đã xóa thành công sinh viên ID {student_id}", "student_id": student_id}

    @staticmethod
    def search_students(db: Session, keyword: str = None, min_age: int = None, max_age: int = None):
        query = db.query(models.StudentModel)
        
        # Tìm kiếm theo từ khóa (Mã SV, Tên hoặc Email)
        if keyword:
            search_pattern = f"%{keyword}%"
            query = query.filter(
                (models.StudentModel.student_code.ilike(search_pattern)) |
                (models.StudentModel.student_name.ilike(search_pattern)) |
                (models.StudentModel.email.ilike(search_pattern))
            )
        
        # Lọc theo khoảng tuổi
        if min_age is not None:
            query = query.filter(models.StudentModel.age >= min_age)
        if max_age is not None:
            query = query.filter(models.StudentModel.age <= max_age)
            
        return query.all()
