# demo5_dependency_injection.py
from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional

app = FastAPI(title="Demo5 - 依赖注入", description="学习代码复用和共享逻辑")


# ========== 简单依赖 ==========
def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
    """公共查询参数"""
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items/")
def list_items(commons: dict = Depends(common_parameters)):
    return {"message": "商品列表", "params": commons}


@app.get("/users/")
def list_users(commons: dict = Depends(common_parameters)):
    return {"message": "用户列表", "params": commons}


# ========== 类作为依赖 ==========
class Pagination:
    def __init__(self, page: int = 1, size: int = 10):
        self.page = page
        self.size = size

    @property
    def skip(self):
        return (self.page - 1) * self.size


@app.get("/products/")
def get_products(pagination: Pagination = Depends()):
    """使用类依赖"""
    return {
        "page": pagination.page,
        "size": pagination.size,
        "skip": pagination.skip,
        "products": [f"产品{i}" for i in range(pagination.skip, pagination.skip + pagination.size)]
    }


# ========== 依赖链 ==========
def get_current_user(token: str = Header(...)):
    """验证token"""
    if token != "secret-token":
        raise HTTPException(status_code=401, detail="无效的token")
    return {"user_id": 1, "username": "alice"}


def get_user_items(current_user: dict = Depends(get_current_user)):
    """获取用户的商品（依赖另一个依赖）"""
    return {"user": current_user, "items": ["item1", "item2"]}


@app.get("/my-items/")
def get_my_items(user_items: dict = Depends(get_user_items)):
    """最终端点，两个依赖都会执行"""
    return user_items


def main():
    import uvicorn
    print("=" * 50)
    print("🚀 Demo5 - 依赖注入启动")
    print("📖 交互文档: http://127.0.0.1:8000/docs")
    print("=" * 50)
    print("🔑 测试 /my-items/ 端点:")
    print("   需要在 Header 中添加: token: secret-token")
    print("   可以在 /docs 页面中点击 'Authorize' 按钮设置")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()