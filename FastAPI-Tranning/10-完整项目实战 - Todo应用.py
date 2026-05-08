# demo10_todo_app.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import secrets

app = FastAPI(title="Demo10 - Todo应用", description="综合实战项目")


# ========== 数据模型 ==========
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 1  # 1-低, 2-中, 3-高


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = None


class Todo(TodoCreate):
    id: int
    completed: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None


# ========== 模拟数据库 ==========
fake_db = []
counter = 1

# ========== 认证 ==========
security = HTTPBasic()


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """简单的HTTP Basic认证"""
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "password")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# ========== API端点 ==========
@app.post("/todos/", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, username: str = Depends(authenticate)):
    """创建Todo（需要认证）"""
    global counter
    new_todo = Todo(
        id=counter,
        title=todo.title,
        description=todo.description,
        priority=todo.priority,
        created_at=datetime.now(),
        completed=False
    )
    fake_db.append(new_todo.dict())
    counter += 1
    return new_todo


@app.get("/todos/", response_model=List[Todo])
def list_todos(
        completed: Optional[bool] = None,
        priority: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
):
    """获取Todo列表，支持过滤"""
    todos = fake_db.copy()

    if completed is not None:
        todos = [t for t in todos if t["completed"] == completed]

    if priority is not None:
        todos = [t for t in todos if t["priority"] == priority]

    return todos[skip:skip + limit]


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    """获取单个Todo"""
    todo = next((t for t in fake_db if t["id"] == todo_id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo不存在")
    return todo


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo_update: TodoUpdate, username: str = Depends(authenticate)):
    """更新Todo（需要认证）"""
    todo = next((t for t in fake_db if t["id"] == todo_id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo不存在")

    update_data = todo_update.dict(exclude_unset=True)
    todo.update(update_data)
    todo["updated_at"] = datetime.now()

    return todo


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, username: str = Depends(authenticate)):
    """删除Todo（需要认证）"""
    global fake_db
    todo = next((t for t in fake_db if t["id"] == todo_id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo不存在")

    fake_db = [t for t in fake_db if t["id"] != todo_id]
    return {"message": "Todo已删除"}


@app.get("/stats/")
def get_stats():
    """获取统计信息"""
    total = len(fake_db)
    completed = len([t for t in fake_db if t["completed"]])
    pending = total - completed

    high_priority = len([t for t in fake_db if t["priority"] == 3])
    medium_priority = len([t for t in fake_db if t["priority"] == 2])
    low_priority = len([t for t in fake_db if t["priority"] == 1])

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": f"{(completed / total * 100):.1f}%" if total > 0 else "0%",
        "by_priority": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority
        }
    }


def main():
    import uvicorn
    print("=" * 60)
    print("🚀 Demo10 - Todo应用启动")
    print("📖 交互文档: http://127.0.0.1:8000/docs")
    print("=" * 60)
    print("🔐 认证信息:")
    print("   用户名: admin")
    print("   密码: password")
    print("=" * 60)
    print("📝 API功能:")
    print("   POST   /todos/     - 创建Todo (需认证)")
    print("   GET    /todos/     - 获取Todo列表")
    print("   GET    /todos/{id} - 获取单个Todo")
    print("   PUT    /todos/{id} - 更新Todo (需认证)")
    print("   DELETE /todos/{id} - 删除Todo (需认证)")
    print("   GET    /stats/     - 统计信息")
    print("=" * 60)
    print("💡 测试步骤:")
    print("   1. 在 /docs 页面点击 'Authorize' 按钮")
    print("   2. 输入用户名: admin, 密码: password")
    print("   3. 先 POST /todos/ 创建几个任务")
    print("   4. 然后 GET /todos/ 查看列表")
    print("   5. 再 GET /stats/ 查看统计")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()