"""
Webhook 系统
支持事件通知和外部系统集成
"""
import asyncio
import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class WebhookEvent(str, Enum):
    """Webhook 事件类型"""
    # 客户事件
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_DELETED = "customer.deleted"
    CUSTOMER_STATUS_CHANGED = "customer.status_changed"
    
    # 文档事件
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_APPROVED = "document.approved"
    DOCUMENT_REJECTED = "document.rejected"
    DOCUMENT_DELETED = "document.deleted"
    
    # 产品事件
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
    PRODUCT_DELETED = "product.deleted"


class WebhookPayload:
    """Webhook 负载"""
    def __init__(
        self,
        event: WebhookEvent,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.event = event
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event": self.event.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class WebhookSubscription:
    """Webhook 订阅"""
    def __init__(
        self,
        url: str,
        events: List[WebhookEvent],
        secret: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        enabled: bool = True
    ):
        self.url = url
        self.events = events
        self.secret = secret
        self.headers = headers or {}
        self.enabled = enabled
    
    def should_trigger(self, event: WebhookEvent) -> bool:
        """检查是否应该触发此订阅"""
        return self.enabled and event in self.events


class WebhookManager:
    """Webhook 管理器 - 单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._subscriptions: List[WebhookSubscription] = []
        self._initialized = True
    
    def subscribe(self, subscription: WebhookSubscription):
        """添加订阅"""
        self._subscriptions.append(subscription)
        logger.info(f"Added webhook subscription for {subscription.url}")
    
    def unsubscribe(self, url: str):
        """移除订阅"""
        self._subscriptions = [s for s in self._subscriptions if s.url != url]
        logger.info(f"Removed webhook subscription for {url}")
    
    def get_subscriptions(self, event: WebhookEvent) -> List[WebhookSubscription]:
        """获取特定事件的所有订阅"""
        return [s for s in self._subscriptions if s.should_trigger(event)]
    
    async def trigger(self, event: WebhookEvent, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        触发 Webhook 事件
        
        Args:
            event: 事件类型
            data: 事件数据
            metadata: 元数据
        """
        payload = WebhookPayload(event, data, metadata=metadata)
        subscriptions = self.get_subscriptions(event)
        
        if not subscriptions:
            logger.debug(f"No subscriptions for event {event.value}")
            return
        
        logger.info(f"Triggering {len(subscriptions)} webhooks for event {event.value}")
        
        # 异步发送所有 webhook
        tasks = [self._send_webhook(sub, payload) for sub in subscriptions]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_webhook(self, subscription: WebhookSubscription, payload: WebhookPayload):
        """
        发送单个 Webhook
        
        Args:
            subscription: 订阅信息
            payload: 负载数据
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "CCD-Webhook/1.0",
                **subscription.headers
            }
            
            # 如果有密钥，添加签名
            if subscription.secret:
                import hmac
                import hashlib
                import json
                
                payload_str = json.dumps(payload.to_dict())
                signature = hmac.new(
                    subscription.secret.encode(),
                    payload_str.encode(),
                    hashlib.sha256
                ).hexdigest()
                headers["X-Webhook-Signature"] = f"sha256={signature}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    subscription.url,
                    json=payload.to_dict(),
                    headers=headers
                )
                
                if response.status_code >= 200 and response.status_code < 300:
                    logger.info(f"Webhook sent successfully to {subscription.url}")
                else:
                    logger.warning(
                        f"Webhook failed with status {response.status_code}: {subscription.url}"
                    )
        
        except Exception as e:
            logger.error(f"Error sending webhook to {subscription.url}: {str(e)}")


# 全局 Webhook 管理器实例
webhook_manager = WebhookManager()


# 便捷函数
async def trigger_webhook(event: WebhookEvent, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
    """
    触发 Webhook 事件的便捷函数
    
    Args:
        event: 事件类型
        data: 事件数据
        metadata: 元数据
    
    Example:
        await trigger_webhook(
            WebhookEvent.CUSTOMER_CREATED,
            {"id": customer.id, "name": customer.name}
        )
    """
    await webhook_manager.trigger(event, data, metadata)


def register_webhook(
    url: str,
    events: List[WebhookEvent],
    secret: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None
):
    """
    注册 Webhook 订阅的便捷函数
    
    Args:
        url: Webhook URL
        events: 订阅的事件列表
        secret: 签名密钥（可选）
        headers: 自定义请求头（可选）
    
    Example:
        register_webhook(
            "https://example.com/webhook",
            [WebhookEvent.CUSTOMER_CREATED, WebhookEvent.CUSTOMER_UPDATED],
            secret="my-secret-key"
        )
    """
    subscription = WebhookSubscription(url, events, secret, headers)
    webhook_manager.subscribe(subscription)


# 示例：在应用启动时注册 webhook
def init_webhooks():
    """初始化 Webhook 订阅"""
    # 这里可以从配置文件或数据库加载 webhook 订阅
    # 示例：
    # register_webhook(
    #     "https://example.com/webhook",
    #     [WebhookEvent.CUSTOMER_CREATED],
    #     secret="your-secret-key"
    # )
    pass

