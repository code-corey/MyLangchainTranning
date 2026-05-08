# demo1_first_api.py
from fastapi import FastAPI

app = FastAPI(title="Demo1 - 第一个API", description="学习路径参数和查询参数")

@app.get("/")
def root():
    """根路径，返回欢迎信息"""
    return {"message": "Hello World", "status": "success"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    """路径参数示例"""
    return {"item_id": item_id, "name": f"商品{item_id}"}

@app.get("/search")
def search_items(q: str, limit: int = 10):
    """查询参数示例"""
    return {"query": q, "limit": limit, "results": [f"结果{i}" for i in range(min(limit, 3))]}

@app.get("/users/{user_id}/items/{item_id}")
def get_user_item(user_id: int, item_id: int):
    """多个路径参数"""
    return {"user_id": user_id, "item_id": item_id}

def main():
    """启动函数"""
    import uvicorn
    print("=" * 50)
    print("🚀 Demo1 - 第一个API启动")
    print("📖 交互文档: http://127.0.0.1:8000/docs")
    print("📖 备用文档: http://127.0.0.1:8000/redoc")
    print("=" * 50)
    print("🔗 测试URL:")
    print("   http://127.0.0.1:8000/")
    print("   http://127.0.0.1:8000/items/123")
    print("   http://127.0.0.1:8000/search?q=phone&limit=5")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()