type EventCallback = (data: any) => void

interface WebSocketMessage {
  type: string
  data?: any
  customer_id?: string
  [key: string]: any
}

class WebSocketService {
  private ws: WebSocket | null = null
  private listeners: Map<string, Set<EventCallback>> = new Map()
  private reconnectTimer: NodeJS.Timeout | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000
  private customerId: string | null = null
  private token: string | null = null

  /**
   * 连接到WebSocket服务器
   * @param customerId 客户ID
   * @param token 认证token
   */
  connect(customerId: string, token: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected')
      return
    }

    this.customerId = customerId
    this.token = token

    const wsUrl = import.meta.env.VITE_API_BASE_URL?.replace('http', 'ws') || 'ws://localhost:8000/api'
    const url = `${wsUrl}/ws/${customerId}?token=${token}`

    console.log('Connecting to WebSocket:', url)

    try {
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        this.emit('connected', { customerId })
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          console.log('WebSocket message received:', message)
          
          // 触发对应类型的事件监听器
          if (message.type) {
            this.emit(message.type, message)
          }
          
          // 触发通用消息监听器
          this.emit('message', message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.emit('error', error)
      }

      this.ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        this.emit('disconnected', { code: event.code, reason: event.reason })
        
        // 尝试重连
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect()
        } else {
          console.log('Max reconnect attempts reached')
          this.emit('max_reconnect_attempts', {})
        }
      }
    } catch (error) {
      console.error('Error creating WebSocket:', error)
      this.scheduleReconnect()
    }
  }

  /**
   * 安排重连
   */
  private scheduleReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * this.reconnectAttempts

    console.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`)

    this.reconnectTimer = setTimeout(() => {
      if (this.customerId && this.token) {
        this.connect(this.customerId, this.token)
      }
    }, delay)
  }

  /**
   * 发送消息
   * @param type 消息类型
   * @param data 消息数据
   */
  send(type: string, data: any = {}) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({ type, data })
      this.ws.send(message)
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  /**
   * 监听事件
   * @param eventType 事件类型
   * @param callback 回调函数
   */
  on(eventType: string, callback: EventCallback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set())
    }
    this.listeners.get(eventType)!.add(callback)
  }

  /**
   * 移除事件监听
   * @param eventType 事件类型
   * @param callback 回调函数
   */
  off(eventType: string, callback: EventCallback) {
    const listeners = this.listeners.get(eventType)
    if (listeners) {
      listeners.delete(callback)
    }
  }

  /**
   * 触发事件
   * @param eventType 事件类型
   * @param data 事件数据
   */
  private emit(eventType: string, data: any) {
    const listeners = this.listeners.get(eventType)
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in event listener for ${eventType}:`, error)
        }
      })
    }
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.customerId = null
    this.token = null
    this.reconnectAttempts = 0
    this.listeners.clear()
  }

  /**
   * 获取连接状态
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }

  /**
   * 获取连接状态文本
   */
  getReadyState(): string {
    if (!this.ws) return 'CLOSED'
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING'
      case WebSocket.OPEN:
        return 'OPEN'
      case WebSocket.CLOSING:
        return 'CLOSING'
      case WebSocket.CLOSED:
        return 'CLOSED'
      default:
        return 'UNKNOWN'
    }
  }
}

// 导出单例
export default new WebSocketService()

