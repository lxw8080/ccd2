import React from 'react'
import { List, Button, Tag, Space, Modal, message, Image } from 'antd'
import { FileOutlined, DownloadOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import type { CustomerDocument } from '../types'

interface DocumentListProps {
  documents: CustomerDocument[]
  customerId: string
  onDelete?: () => void
}

const DocumentList: React.FC<DocumentListProps> = ({ documents, customerId, onDelete }) => {
  const queryClient = useQueryClient()

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (documentId: string) => {
      await api.delete(`/api/documents/${documentId}`)
    },
    onSuccess: () => {
      message.success('文件删除成功')
      queryClient.invalidateQueries({ queryKey: ['documents', customerId] })
      if (onDelete) onDelete()
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败')
    },
  })

  const handleDelete = (document: CustomerDocument) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文件 "${document.file_name}" 吗？`,
      okText: '确定',
      cancelText: '取消',
      onOk: () => deleteMutation.mutate(document.id),
    })
  }

  const handleDownload = (document: CustomerDocument) => {
    // 创建下载链接
    const link = document.createElement('a')
    link.href = document.file_url || `/api/documents/${document.id}/download`
    link.download = document.file_name
    link.click()
  }

  const handlePreview = (document: CustomerDocument) => {
    if (document.file_type.startsWith('image/')) {
      // 图片预览
      Modal.info({
        title: document.file_name,
        width: 800,
        content: (
          <Image
            src={document.file_url || `/api/documents/${document.id}/download`}
            alt={document.file_name}
            style={{ maxWidth: '100%' }}
          />
        ),
      })
    } else {
      // 其他文件直接下载
      handleDownload(document)
    }
  }

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      pending: { color: 'default', text: '待审核' },
      approved: { color: 'success', text: '已通过' },
      rejected: { color: 'error', text: '已拒绝' },
    }
    const config = statusMap[status] || { color: 'default', text: status }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  return (
    <List
      dataSource={documents}
      renderItem={(document) => (
        <List.Item
          actions={[
            <Button
              key="preview"
              type="link"
              icon={<EyeOutlined />}
              onClick={() => handlePreview(document)}
            >
              预览
            </Button>,
            <Button
              key="download"
              type="link"
              icon={<DownloadOutlined />}
              onClick={() => handleDownload(document)}
            >
              下载
            </Button>,
            <Button
              key="delete"
              type="link"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDelete(document)}
              loading={deleteMutation.isPending}
            >
              删除
            </Button>,
          ]}
        >
          <List.Item.Meta
            avatar={<FileOutlined style={{ fontSize: 24 }} />}
            title={
              <Space>
                {document.file_name}
                {getStatusTag(document.status)}
              </Space>
            }
            description={
              <Space direction="vertical" size={0}>
                <span>大小: {formatFileSize(document.file_size)}</span>
                <span>上传时间: {new Date(document.created_at).toLocaleString('zh-CN')}</span>
                {document.review_note && (
                  <span style={{ color: '#ff4d4f' }}>审核意见: {document.review_note}</span>
                )}
              </Space>
            }
          />
        </List.Item>
      )}
    />
  )
}

export default DocumentList

