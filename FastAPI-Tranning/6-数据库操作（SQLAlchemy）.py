# demo6_database.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Demo6 - 数据库操作", description="学习SQLAlchemy集成")

# ========== 数据库配置 ==========
SQLALCHEMY_DATABASE_URL = "sqlite:///./demo6.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ========== SQLAlchemy模型 ==========
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


# ========== Pydantic模型 ==========
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 创建表 ==========
Base.metadata.create_all(bind=engine)


# ========== 依赖 ==========
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== API端点 ==========
@app.post("/users/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建用户"""
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    db_user = UserDB(
        username=user.username,
        email=user.email,
        hashed_password=f"hashed_{user.password}"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=List[UserOut])
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """获取用户列表"""
    users = db.query(UserDB).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取单个用户"""
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    db.delete(user)
    db.commit()
    return {"message": "用户已删除"}


def main():
    import uvicorn
    print("=" * 50)
    print("🚀 Demo6 - 数据库操作启动")
    print("📖 交互文档: http://127.0.0.1:8000/docs")
    print("=" * 50)
    print("💾 数据库文件: demo6.db")
    print("📝 测试步骤:")
    print("   1. POST /users/ 创建用户")
    print("   2. GET /users/ 查看用户列表")
    print("   3. GET /users/{id} 查看单个用户")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()