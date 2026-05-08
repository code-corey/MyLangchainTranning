# demo3_parameters.py
from fastapi import FastAPI, Query, Path
from typing import Optional, List
from enum import Enum

app = FastAPI(title="Demo3 - 参数详解", description="学习各种参数类型和验证")

# 枚举类型参数
class ModelName(str, Enum):
    ALEXNET = "alexnet"
    RESNET = "resnet"
    LENET = "lenet"

@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    """枚举路径参数"""
    if model_name == ModelName.ALEXNET:
        return {"model_name": model_name, "message": "AlexNet - 深度学习鼻祖"}
    elif model_name == ModelName.RESNET:
        return {"model_name": model_name, "message": "ResNet - 残差网络"}
    else:
        return {"model_name": model_name, "message": "LeNet - 卷积神经网络先驱"}

@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    """接收完整路径作为参数"""
    return {"file_path": file_path}

@app.get("/products/")
def list_products(
    category: str = Query(..., min_length=2, max_length=20, description="产品分类"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("price", regex="^(price|rating|name)$", description="排序字段"),
    min_price: Optional[float] = Query(None, ge=0, description="最低价格"),
    tags: List[str] = Query(default=[], description="标签筛选")
):
    """带验证的查询参数"""
    return {
        "category": category,
        "page": page,
        "size": size,
        "sort_by": sort_by,
        "min_price": min_price,
        "tags": tags,
        "results": [f"Product {i}" for i in range(size)]
    }

@app.get("/users/{user_id}/orders")
def get_user_orders(
    user_id: int = Path(..., gt=0, description="用户ID"),
    status: str = Query("pending", regex="^(pending|paid|shipped|delivered)$"),
    limit: int = Query(10, le=50)
):
    """混合路径参数和查询参数"""
    return {
        "user_id": user_id,
        "status": status,
        "limit": limit,
        "orders": [f"订单{i}" for i in range(min(limit, 5))]
    }

def main():
    import uvicorn
    print("=" * 50)
    print("🚀 Demo3 - 参数详解启动")
    print("📖 交互文档: http://127.0.0.1:8000/docs")
    print("=" * 50)
    print("🔗 测试URL示例:")
    print("   http://127.0.0.1:8000/models/resnet")
    print("   http://127.0.0.1:8000/files/home/user/data.txt")
    print("   http://127.0.0.1:8000/products/?category=electronics&tags=wireless&tags=bluetooth")
    print("   http://127.0.0.1:8000/users/123/orders?status=paid&limit=20")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()