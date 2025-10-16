from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import logging
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储每个客户的活跃连接: {customer_id: Set[WebSocket]}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # 存储每个用户的连接: {user_id: Set[WebSocket]}
        self.user_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, customer_id: str, user_id: str):
        """接受WebSocket连接"""
        await websocket.accept()
        
        # 添加到客户连接池
        if customer_id not in self.active_connections:
            self.active_connections[customer_id] = set()
        self.active_connections[customer_id].add(websocket)
        
        # 添加到用户连接池
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        logger.info(f"WebSocket connected: customer={customer_id}, user={user_id}")
    
    def disconnect(self, websocket: WebSocket, customer_id: str, user_id: str):
        """断开WebSocket连接"""
        # 从客户连接池移除
        if customer_id in self.active_connections:
            self.active_connections[customer_id].discard(websocket)
            if not self.active_connections[customer_id]:
                del self.active_connections[customer_id]
        
        # 从用户连接池移除
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected: customer={customer_id}, user={user_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        await websocket.send_json(message)
    
    async def broadcast_to_customer(self, customer_id: str, message: dict, exclude: WebSocket = None):
        """向关注某个客户的所有连接广播消息"""
        if customer_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[customer_id]:
                if connection != exclude:
                    try:
                        await connection.send_json(message)
                    except Exception as e:
                        logger.error(f"Error sending message: {e}")
                        disconnected.add(connection)
            
            # 清理断开的连接
            for connection in disconnected:
                self.active_connections[customer_id].discard(connection)
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        """向某个用户的所有连接广播消息"""
        if user_id in self.user_connections:
            disconnected = set()
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    disconnected.add(connection)
            
            # 清理断开的连接
            for connection in disconnected:
                self.user_connections[user_id].discard(connection)
    
    def get_customer_connection_count(self, customer_id: str) -> int:
        """获取某个客户的连接数"""
        return len(self.active_connections.get(customer_id, set()))


# 全局连接管理器实例
manager = ConnectionManager()


@router.websocket("/ws/{customer_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    customer_id: str,
):
    """
    WebSocket端点
    客户端连接时需要提供token作为查询参数: /ws/{customer_id}?token=xxx
    """
    # 从查询参数获取token
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return
    
    # 验证token并获取用户信息
    try:
        # 这里简化处理，实际应该验证JWT token
        # user = await get_current_user_from_token(token)
        # 暂时使用一个模拟的user_id
        user_id = "temp_user"  # TODO: 从token解析真实user_id
    except Exception as e:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    await manager.connect(websocket, customer_id, user_id)
    
    try:
        # 发送欢迎消息
        await manager.send_personal_message({
            "type": "connected",
            "message": f"Connected to customer {customer_id}",
            "customer_id": customer_id,
            "connection_count": manager.get_customer_connection_count(customer_id)
        }, websocket)
        
        # 通知其他连接有新用户加入
        await manager.broadcast_to_customer(customer_id, {
            "type": "user_joined",
            "customer_id": customer_id,
            "connection_count": manager.get_customer_connection_count(customer_id)
        }, exclude=websocket)
        
        # 保持连接并处理消息
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 广播消息给其他连接
            await manager.broadcast_to_customer(customer_id, {
                "type": "message",
                "data": message_data,
                "customer_id": customer_id
            }, exclude=websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, customer_id, user_id)
        
        # 通知其他连接有用户离开
        await manager.broadcast_to_customer(customer_id, {
            "type": "user_left",
            "customer_id": customer_id,
            "connection_count": manager.get_customer_connection_count(customer_id)
        })
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, customer_id, user_id)


# 辅助函数：在其他API中调用以广播事件
async def broadcast_document_uploaded(customer_id: str, document_data: dict):
    """广播文档上传事件"""
    await manager.broadcast_to_customer(customer_id, {
        "type": "document_uploaded",
        "customer_id": customer_id,
        "data": document_data
    })


async def broadcast_document_deleted(customer_id: str, document_id: str):
    """广播文档删除事件"""
    await manager.broadcast_to_customer(customer_id, {
        "type": "document_deleted",
        "customer_id": customer_id,
        "document_id": document_id
    })


async def broadcast_customer_updated(customer_id: str, customer_data: dict):
    """广播客户信息更新事件"""
    await manager.broadcast_to_customer(customer_id, {
        "type": "customer_updated",
        "customer_id": customer_id,
        "data": customer_data
    })

