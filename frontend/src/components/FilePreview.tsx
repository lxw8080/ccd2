import React, { useState, useEffect } from 'react'
import { Modal, Button, Space, Image, Spin, Alert, Typography } from 'antd'
import { LeftOutlined, RightOutlined, DownloadOutlined, CloseOutlined } from '@ant-design/icons'
import PDFViewer from './PDFViewer'

const { Text } = Typography

interface FilePreviewProps {
  visible: boolean
  onClose: () => void
  fileUrl: string
  fileName: string
  fileType?: string
  files?: Array<{
    id: string
    file_name: string
    file_url?: string
    file_type?: string
  }>
  currentFileId?: string
  onFileChange?: (fileId: string) => void
  onDownload?: () => void
}

const FilePreview: React.FC<FilePreviewProps> = ({
  visible,
  onClose,
  fileUrl,
  fileName,
  fileType,
  files = [],
  currentFileId,
  onFileChange,
  onDownload,
}) => {
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string>('')
  const [blobUrl, setBlobUrl] = useState<string | null>(null)

  // 重置状态
  useEffect(() => {
    if (visible) {
      setLoading(true)
      setError('')
    }
  }, [visible, fileUrl])

  // 获取文件并创建 blob URL（用于带认证的文件请求）
  useEffect(() => {
    if (!visible || !fileUrl) return

    const currentFileType = getFileType()
    if (currentFileType === 'other') return

    // 清理旧的 blob URL
    if (blobUrl) {
      URL.revokeObjectURL(blobUrl)
      setBlobUrl(null)
    }

    const fetchFile = async () => {
      try {
        setLoading(true)
        setError('')

        // 从 localStorage 获取 token
        const authStorage = localStorage.getItem('auth-storage')
        const token = authStorage ? JSON.parse(authStorage).state.token : null

        const response = await fetch(fileUrl, {
          headers: token ? {
            'Authorization': `Bearer ${token}`
          } : {}
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        setBlobUrl(url)
        // 不要在这里设置 loading 为 false - 让 onDocumentLoadSuccess/onImageLoad 处理
        // 对于 PDF，loading 将在 onDocumentLoadSuccess 中设置为 false
        // 对于图片，loading 将在 onImageLoad 中设置为 false
      } catch (err) {
        console.error('Failed to fetch file:', err)
        const errorMsg = currentFileType === 'image'
          ? '图片加载失败，请尝试下载后查看'
          : 'PDF 加载失败，请尝试下载后查看'
        setError(errorMsg)
        setLoading(false)
      }
    }

    fetchFile()

    // 清理函数
    return () => {
      if (blobUrl) {
        URL.revokeObjectURL(blobUrl)
      }
    }
  }, [visible, fileUrl])

  // 判断文件类型
  const getFileType = (): 'image' | 'pdf' | 'other' => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    const type = fileType?.toLowerCase()

    if (ext && ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)) {
      return 'image'
    }
    if (ext === 'pdf' || type?.includes('pdf')) {
      return 'pdf'
    }
    return 'other'
  }

  const currentFileType = getFileType()

  // 图片加载完成
  const onImageLoad = () => {
    setLoading(false)
  }

  // 图片加载失败
  const onImageError = (e: any) => {
    console.error('Image load error:', e)
    setError('图片加载失败，请尝试下载后查看')
    setLoading(false)
  }

  // PDF iframe 加载完成
  const onPdfLoad = () => {
    setLoading(false)
  }

  // PDF iframe 加载失败
  const onPdfError = () => {
    setError('PDF 加载失败，请尝试下载后查看')
    setLoading(false)
  }

  // 切换文件
  const handleFileChange = (direction: 'prev' | 'next') => {
    if (!files.length || !currentFileId || !onFileChange) return

    const currentIndex = files.findIndex(f => f.id === currentFileId)
    if (currentIndex === -1) return

    let newIndex = direction === 'prev' ? currentIndex - 1 : currentIndex + 1
    if (newIndex < 0) newIndex = files.length - 1
    if (newIndex >= files.length) newIndex = 0

    onFileChange(files[newIndex].id)
  }

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!visible) return

      if (e.key === 'ArrowLeft') {
        handleFileChange('prev')
      } else if (e.key === 'ArrowRight') {
        handleFileChange('next')
      } else if (e.key === 'Escape') {
        onClose()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [visible, currentFileId, files])

  // 渲染预览内容
  const renderPreviewContent = () => {
    if (error) {
      return (
        <Alert
          message="加载失败"
          description={error}
          type="error"
          showIcon
          action={
            onDownload && (
              <Button size="small" onClick={onDownload}>
                下载文件
              </Button>
            )
          }
        />
      )
    }

    if (currentFileType === 'image') {
      return (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          {loading && (
            <div style={{ padding: '100px 0' }}>
              <Spin size="large" tip="加载中..." />
            </div>
          )}
          {error ? (
            <Alert
              message="加载失败"
              description={error}
              type="error"
              showIcon
              action={
                onDownload && (
                  <Button type="primary" onClick={onDownload}>
                    下载文件
                  </Button>
                )
              }
            />
          ) : blobUrl ? (
            <img
              src={blobUrl}
              alt={fileName}
              onLoad={onImageLoad}
              onError={onImageError}
              style={{
                maxWidth: '100%',
                maxHeight: 'calc(100vh - 300px)',
                display: 'block',
                margin: '0 auto'
              }}
            />
          ) : null}
        </div>
      )
    }

    if (currentFileType === 'pdf') {
      return (
        <div style={{ textAlign: 'center', position: 'relative' }}>
          {error ? (
            <Alert
              message="加载失败"
              description={error}
              type="error"
              showIcon
              action={
                onDownload && (
                  <Button type="primary" onClick={onDownload}>
                    下载文件
                  </Button>
                )
              }
            />
          ) : blobUrl ? (
            <PDFViewer
              fileUrl={blobUrl}
              fileName={fileName}
              onLoadError={() => {
                setError('PDF 加载失败，请尝试下载后查看')
                setLoading(false)
              }}
            />
          ) : (
            <div style={{ padding: '100px 0' }}>
              <Spin size="large" tip="加载 PDF..." />
            </div>
          )}
        </div>
      )
    }

    // 其他文件类型
    return (
      <Alert
        message="不支持预览此文件类型"
        description={
          <div>
            <p>文件名：{fileName}</p>
            <p>文件类型：{fileType || '未知'}</p>
            <p>请下载后使用相应的应用程序打开。</p>
          </div>
        }
        type="info"
        showIcon
        action={
          onDownload && (
            <Button type="primary" onClick={onDownload}>
              下载文件
            </Button>
          )
        }
      />
    )
  }

  // 获取当前文件索引
  const getCurrentFileIndex = () => {
    if (!files.length || !currentFileId) return null
    const index = files.findIndex(f => f.id === currentFileId)
    return index >= 0 ? index + 1 : null
  }

  const currentIndex = getCurrentFileIndex()

  return (
    <Modal
      title={
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Text strong>{fileName}</Text>
          {files.length > 1 && currentIndex && (
            <Text type="secondary" style={{ fontSize: 14 }}>
              {currentIndex} / {files.length}
            </Text>
          )}
        </Space>
      }
      open={visible}
      onCancel={onClose}
      width={Math.min(window.innerWidth - 100, 900)}
      style={{ top: 20 }}
      footer={
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            {files.length > 1 && (
              <>
                <Button
                  icon={<LeftOutlined />}
                  onClick={() => handleFileChange('prev')}
                >
                  上一个
                </Button>
                <Button
                  icon={<RightOutlined />}
                  onClick={() => handleFileChange('next')}
                >
                  下一个
                </Button>
              </>
            )}
          </Space>
          <Space>
            {onDownload && (
              <Button icon={<DownloadOutlined />} onClick={onDownload}>
                下载
              </Button>
            )}
            <Button icon={<CloseOutlined />} onClick={onClose}>
              关闭
            </Button>
          </Space>
        </Space>
      }
    >
      <div style={{ maxHeight: 'calc(100vh - 300px)', overflowY: 'auto' }}>
        {renderPreviewContent()}
      </div>
    </Modal>
  )
}

export default FilePreview

