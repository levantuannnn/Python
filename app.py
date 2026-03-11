# Import FastAPI để tạo API server
from fastapi import FastAPI, HTTPException, Depends

# SQLAlchemy dùng để làm việc với database theo kiểu ORM (không cần viết SQL nhiều)
from sqlalchemy import create_engine, Column, Integer, String

# Tạo class base cho các model database
from sqlalchemy.ext.declarative import declarative_base

# Session dùng để giao tiếp với database
from sqlalchemy.orm import sessionmaker, Session

# Pydantic dùng để validate dữ liệu request/response
from pydantic import BaseModel

# List dùng để khai báo kiểu dữ liệu trả về là danh sách
from typing import List


# Tạo engine kết nối database SQLite
# connect_args cần thiết cho SQLite vì FastAPI chạy multi-thread
engine = create_engine("sqlite:///users.db", connect_args={"check_same_thread": False})


# Tạo SessionLocal để mỗi request API có một session riêng làm việc với database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base là lớp cha để các bảng database kế thừa
# SQLAlchemy cần Base để biết class nào là table
Base = declarative_base()



# ================= DATABASE MODEL =================
# Model này mô tả cấu trúc bảng trong database

class User(Base):
    # Tên bảng trong database
    __tablename__ = "users"

    # id là khóa chính
    id = Column(Integer, primary_key=True, index=True)

    # name không được null
    name = Column(String, nullable=False)

    # email phải unique để tránh trùng tài khoản
    email = Column(String, unique=True, nullable=False)

    # role dùng để phân quyền user
    role = Column(String, nullable=False)


# Lệnh này tạo bảng trong database nếu bảng chưa tồn tại
Base.metadata.create_all(bind=engine)



# ================= API MODELS =================
# Các class này dùng để validate dữ liệu API

class UserCreate(BaseModel):
    # Dữ liệu client gửi lên khi tạo user
    name: str
    email: str
    role: str


class UserResponse(BaseModel):
    # Dữ liệu trả về cho client
    id: int
    name: str
    email: str
    role: str

    class Config:
        # Cho phép Pydantic đọc dữ liệu từ object SQLAlchemy
        from_attributes = True



# ================= DATABASE SESSION =================
# Hàm này tạo database session cho mỗi request API

def get_db():
    db = SessionLocal()  # mở kết nối database
    try:
        yield db          # trả session cho API sử dụng
    finally:
        db.close()        # đóng session sau khi request kết thúc



# Tạo FastAPI application
app = FastAPI(title="Code with Josh")



# ================= API ENDPOINTS =================

# API test server
@app.get("/")
def root():
    return {"message": "FastAPI Tutorial with SQLAlchemy!"}



# Lấy danh sách user
@app.get("/users/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):

    # db.query(User) -> SELECT * FROM users
    return db.query(User).all()



# Lấy user theo ID
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):

    # tìm user theo id
    user = db.query(User).filter(User.id == user_id).first()

    # nếu không có user thì trả lỗi 404
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user



# Tạo user mới
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    # kiểm tra email đã tồn tại chưa
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # tạo object User từ dữ liệu client gửi lên
    db_user = User(**user.dict())

    # thêm vào database
    db.add(db_user)

    # commit để lưu dữ liệu
    db.commit()

    # refresh để lấy dữ liệu mới nhất (ví dụ id auto tăng)
    db.refresh(db_user)

    return db_user



# Update user
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):

    # tìm user
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # cập nhật từng field
    for field, value in user.dict().items():
        setattr(db_user, field, value)

    # lưu thay đổi
    db.commit()

    # load lại dữ liệu
    db.refresh(db_user)

    return db_user



# Delete user
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):

    # tìm user
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # xóa user
    db.delete(user)

    # commit để lưu thay đổi
    db.commit()

    return {"message": "User deleted"}