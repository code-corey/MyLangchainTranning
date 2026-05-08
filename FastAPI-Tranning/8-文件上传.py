# demo8_file_upload.py
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from typing import List
import shutil
from pathlib import Path

app = FastAPI(title="Demo8 - 文件上传", description="学习文件上传和处理")

# 创建上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ========== 文件上传端点 ==========
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """上传单个文件"""
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "文件上传成功",
        "filename": file.filename,
        "size": file_path.stat().st_size
    }


@app.post("/upload-multiple/")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """同时上传多个文件"""
    saved_files = []
    for file in files:
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append({"filename": file.filename, "size": file_path.stat().st_size})

    return {"message": f"成功上传 {len(files)} 个文件", "files": saved_files}


@app.post("/post-with-image/")
async def create_post(
        title: str = Form(...),
        content: str = Form(...),
        image: UploadFile = File(...)
):
    """文章+图片混合表单"""
    image_path = UPLOAD_DIR / f"{title}_{image.filename}"
    with image_path.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return {
        "title": title,
        "content": content,
        "image_url": f"/download/{image_path.name}"
    }


# ========== 文件下载和列表 ==========
@app.get("/download/{filename}")
async def download_file(filename: str):
    """下载文件"""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(path=file_path, filename=filename)


@app.get("/files/")
async def list_files():
    """列出所有上传的文件"""
    files = []
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
    return {"files": files}


# ========== HTML表单页面 ==========
@app.get("/", response_class=HTMLResponse)
async def upload_form():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>文件上传测试</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; }
            .form-group { margin: 20px 0; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>📁 FastAPI 文件上传测试</h1>

        <div class="form-group">
            <h3>1. 单个文件上传</h3>
            <form action="/upload/" method="post" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <button type="submit">上传</button>
            </form>
        </div>

        <div class="form-group">
            <h3>2. 多个文件上传</h3>
            <form action="/upload-multiple/" method="post" enctype="multipart/form-data">
                <input type="file" name="files" multiple required>
                <button type="submit">上传多个</button>
            </form>
        </div>

        <div class="form-group">
            <h3>3. 文章+图片</h3>
            <form action="/post-with-image/" method="post" enctype="multipart/form-data">
                <input type="text" name="title" placeholder="标题" required><br><br>
                <textarea name="content" placeholder="内容" rows="3"></textarea><br><br>
                <input type="file" name="image" accept="image/*" required><br><br>
                <button type="submit">发布</button>
            </form>
        </div>

        <div>
            <a href="/files/">查看所有文件</a>
        </div>
    </body>
    </html>
    """


def main():
    import uvicorn
    print("=" * 50)
    print("🚀 Demo8 - 文件上传启动")
    print("📖 交互文档: http://127.0.0.1:8000/docs")
    print("🌐 HTML测试页面: http://127.0.0.1:8000/")
    print("=" * 50)
    print(f"📁 上传文件保存目录: {UPLOAD_DIR.absolute()}")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()