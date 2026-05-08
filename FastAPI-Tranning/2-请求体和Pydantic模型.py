# demo2_request_body.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

app = FastAPI(title="Demo2 - 用户管理API", description="学习Pydantic模型和POST请求")


# 定义数据模型
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    email: str = Field(..., description="邮箱地址")
    age: int = Field(ge=0, le=150, description="年龄")
    is_active: bool = Field(default=True, description="是否激活")
    tags: List[str] = Field(default=[], description="用户标签")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    age: int
    is_active: bool
    created_at: datetime


# 模拟数据库
fake_db = []
counter = 1


@app.post("/users/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    """创建新用户"""
    global counter

    # 检查用户名是否已存在
    for existing in fake_db:
        if existing["username"] == user.username:
            raise HTTPException(status_code=400, detail="用户名已存在")

    # 创建新用户
    new_user = {
        "id": counter,
        "username": user.username,
        "email": user.email,
        "age": user.age,
        "is_active": user.is_active,
        "created_at": datetime.now(),
    }
    fake_db.append(new_user)
    counter += 1
    return new_user


@app.get("/users/")
def list_users(skip: int = 0, limit: int = 10):
    """获取用户列表"""
    return {"users": fake_db[skip:skip + limit], "total": len(fake_db)}


def main():
    import uvicorn
    print("=" * 50)
    print("🚀 Demo2 - 请求体和Pydantic启动")
    print("📖 交互文档: http://127.0.0.1:8000/docs")
    print("=" * 50)
    print("📝 测试POST请求示例:")
    print("   在 /docs 页面中找到 /users/ POST")
    print("   点击 'Try it out' 按钮")
    print("   输入以下JSON:")
    print("   {")
    print('       "username": "alice",')
    print('       "email": "alice@example.com",')
    print('       "age": 25,')
    print('       "tags": ["python", "fastapi"]')
    print("   }")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()