# demo4_response_model.py
from fastapi import FastAPI, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

app = FastAPI(title="Demo4 - 响应模型", description="学习如何控制API输出")

# 内部使用的完整模型
class UserInDB(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    hashed_password: str
    created_at: datetime
    is_active: bool = True

# 对外返回的模型（不包含密码）
class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool

# 嵌套响应模型
class Item(BaseModel):
    name: str
    price: float

class UserWithItems(UserOut):
    items: List[Item] = []

@app.post("/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserInDB):
    """创建用户，返回不包含密码的信息"""
    return user

@app.get("/users/{username}", response_model=UserWithItems)
def get_user_with_items(username: str):
    """获取用户及其订单"""
    return {
        "username": username,
        "email": f"{username}@example.com",
        "full_name": username.title(),
        "created_at": datetime.now(),
        "is_active": True,
        "items": [
            {"name": "商品1", "price": 99.9},
            {"name": "商品2", "price": 199.9}
        ]
    }

# 排除空值
class Product(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    discount: Optional[float] = None

@app.get("/products/{product_id}", response_model=Product, response_model_exclude_unset=True)
def get_product(product_id: int):
    """返回时自动排除未设置的字段"""
    return {
        "name": f"产品{product_id}",
        "price": 100.0
        # description和discount未设置，不会出现在响应中
    }

def main():
    import uvicorn
    print("=" * 50)
    print("🚀 Demo4 - 响应模型启动")
    print("📖 交互文档: http://127.0.0.1:8000/docs")
    print("=" * 50)
    print("💡 观察重点:")
    print("   1. POST /users/ 响应中不包含 hashed_password 字段")
    print("   2. GET /products/1 响应中不包含未设置的字段 (description, discount)")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()