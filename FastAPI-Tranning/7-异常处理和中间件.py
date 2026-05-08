# demo7_exceptions_middleware.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(title="Demo7 - 异常处理", description="学习全局异常处理和中间件")

# ========== 添加CORS中间件 ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 自定义中间件：请求日志 ==========
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录每个请求的处理时间"""
    start_time = time.time()
    print(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"📤 {response.status_code} - 耗时: {process_time:.3f}s")
    return response

# ========== 自定义异常类 ==========
class BusinessError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

# ========== 全局异常处理器 ==========
@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    return JSONResponse(
        status_code=400,
        content={"error_code": exc.code, "message": exc.message, "type": "business_error"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    return JSONResponse(status_code=422, content={"detail": "请求验证失败", "errors": errors})

# ========== 测试端点 ==========
@app.get("/items/{item_id}")
def get_item(item_id: int):
    """普通端点"""
    if item_id < 0:
        raise HTTPException(status_code=400, detail="ID不能为负数")
    if item_id == 404:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {"item_id": item_id, "name": f"商品{item_id}"}

@app.get("/business-error")
def trigger_business_error():
    """触发业务异常"""
    raise BusinessError(code=1001, message="库存不足")

@app.get("/validation-error")
def validation_error(value: int):
    """触发验证错误（传字符串会报错）"""
    return {"value": value}

def main():
    import uvicorn
    print("=" * 50)
    print("🚀 Demo7 - 异常处理和中间件启动")
    print("📖 交互文档: http://127.0.0.1:8000/docs")
    print("=" * 50)
    print("🧪 测试异常:")
    print("   http://127.0.0.1:8000/items/-1  (触发400)")
    print("   http://127.0.0.1:8000/items/404 (触发404)")
    print("   http://127.0.0.1:8000/business-error (触发业务异常)")
    print("   http://127.0.0.1:8000/validation-error?value=abc (触发验证错误)")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()