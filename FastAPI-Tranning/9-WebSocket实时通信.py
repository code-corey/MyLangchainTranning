# demo9_websocket.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict
import json
from datetime import datetime

app = FastAPI(title="Demo9 - WebSocket", description="学习WebSocket实时通信")


# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, message: str, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)


manager = ConnectionManager()


# WebSocket聊天室端点
@app.websocket("/ws/chat/{room_id}/{username}")
async def websocket_chat(websocket: WebSocket, room_id: str, username: str):
    await manager.connect(websocket, room_id)

    # 发送欢迎消息
    await manager.broadcast(
        json.dumps({"type": "system", "username": "系统", "message": f"{username} 加入了房间",
                    "time": datetime.now().strftime("%H:%M:%S")}),
        room_id
    )

    try:
        while True:
            data = await websocket.receive_text()
            message_data = {
                "type": "chat",
                "username": username,
                "message": data,
                "time": datetime.now().strftime("%H:%M:%S")
            }
            await manager.broadcast(json.dumps(message_data), room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(
            json.dumps({"type": "system", "username": "系统", "message": f"{username} 离开了房间",
                        "time": datetime.now().strftime("%H:%M:%S")}),
            room_id
        )


# 简单回声WebSocket
@app.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("客户端断开连接")


# HTML聊天室页面
@app.get("/", response_class=HTMLResponse)
async def get_chat_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket聊天室</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; }
            #chat { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
            .system { color: gray; font-style: italic; }
            .chat { margin: 5px 0; }
            .username { font-weight: bold; color: #007bff; }
            .time { color: gray; font-size: 12px; margin-left: 10px; }
            input { padding: 10px; width: 80%; }
            button { padding: 10px 20px; }
        </style>
    </head>
    <body>
        <h1>💬 WebSocket聊天室</h1>
        <div>
            <input type="text" id="username" placeholder="用户名" value="User" style="width: 200px;">
            <input type="text" id="room" placeholder="房间号" value="room1" style="width: 200px;">
            <button onclick="connect()">连接</button>
            <button onclick="disconnect()">断开</button>
        </div>
        <div id="chat"></div>
        <div>
            <input type="text" id="message" placeholder="输入消息..." onkeypress="if(event.keyCode==13) send()">
            <button onclick="send()">发送</button>
        </div>

        <script>
            let ws = null;

            function connect() {
                const username = document.getElementById('username').value;
                const room = document.getElementById('room').value;
                ws = new WebSocket(`ws://localhost:8000/ws/chat/${room}/${username}`);

                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    const chat = document.getElementById('chat');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = data.type === 'system' ? 'system' : 'chat';
                    messageDiv.innerHTML = data.type === 'system' ? 
                        `<span>${data.message}</span>` :
                        `<span class="username">${data.username}</span><span class="time">${data.time}</span><br>${data.message}`;
                    chat.appendChild(messageDiv);
                    chat.scrollTop = chat.scrollHeight;
                };

                ws.onclose = function() {
                    addSystemMessage('连接已断开');
                };
            }

            function disconnect() {
                if (ws) ws.close();
                ws = null;
            }

            function send() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = document.getElementById('message').value;
                    ws.send(message);
                    document.getElementById('message').value = '';
                }
            }

            function addSystemMessage(msg) {
                const chat = document.getElementById('chat');
                const div = document.createElement('div');
                div.className = 'system';
                div.innerHTML = `<span>${msg}</span>`;
                chat.appendChild(div);
            }
        </script>
    </body>
    </html>
    """


def main():
    import uvicorn
    print("=" * 50)
    print("🚀 Demo9 - WebSocket启动")
    print("📖 交互文档: http://127.0.0.1:8000/docs")
    print("🌐 聊天室页面: http://127.0.0.1:8000/")
    print("=" * 50)
    print("💡 使用说明:")
    print("   1. 打开多个浏览器窗口访问聊天室页面")
    print("   2. 输入用户名和房间号")
    print("   3. 点击连接，即可开始聊天")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()