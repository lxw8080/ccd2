import React, { useState } from 'react'
import { Card, Progress, Tag, Button, Space, List, Typography, Grid, Collapse, Alert, Modal, message } from 'antd'
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  UploadOutlined,
  EyeOutlined,
  DeleteOutlined,
  DownloadOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons'
import type { DetailedCompletenessResult, DetailedDocumentTypeInfo, DetailedDocumentInfo } from '../types'
import { api } from '../services/api'
import FilePreview from './FilePreview'

const { Title, Text } = Typography
const { Panel } = Collapse
const { useBreakpoint } = Grid

interface DetailedCompletenessViewProps {
  completeness: DetailedCompletenessResult
  onUpload: (documentTypeId: string) => void
  onRefresh: () => void
}

const DetailedCompletenessView: React.FC<DetailedCompletenessViewProps> = ({
  completeness,
  onUpload,
  onRefresh,
}) => {
  const screens = useBreakpoint()
  const isMobile = !screens.md
  const [deletingDocId, setDeletingDocId] = useState<string | null>(null)

  // Calculate progress
  const progress = completeness.total_required > 0
    ? Math.round((completeness.approved_required / completeness.total_required) * 100)
    : 100

  // Get progress status
  const getProgressStatus = () => {
    if (progress === 100) return 'success'
    if (progress >= 50) return 'active'
    return 'exception'
  }

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'success'
      case 'pending':
        return 'processing'
      case 'rejected':
        return 'error'
      case 'not_uploaded':
        return 'default'
      default:
        return 'default'
    }
  }

  // Get status text
  const getStatusText = (status: string) => {
    switch (status) {
      case 'approved':
        return '已通过'
      case 'pending':
        return '待审核'
      case 'rejected':
        return '已拒绝'
      case 'not_uploaded':
        return '未上传'
      default:
        return status
    }
  }

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  // Format date
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Handle preview
  const handlePreview = (doc: DetailedDocumentInfo, allDocs: DetailedDocumentInfo[]) => {
    setPreviewFile(doc)
    setPreviewFiles(allDocs)
    setPreviewFileUrl(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/download/${doc.id}?inline=true`)
    setPreviewVisible(true)
  }

  // Handle file change in preview
  const handlePreviewFileChange = (fileId: string) => {
    const file = previewFiles.find(f => f.id === fileId)
    if (file) {
      setPreviewFile(file)
      setPreviewFileUrl(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/download/${file.id}?inline=true`)
    }
  }

  // Handle download
  const handleDownload = async (doc: DetailedDocumentInfo) => {
    try {
      const response = await api.get(`/api/documents/download/${doc.id}`, {
        responseType: 'blob',
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', doc.file_name)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

      message.success('下载成功')
    } catch (error) {
      message.error('下载失败')
    }
  }

  // Handle download from preview
  const handleDownloadFromPreview = async () => {
    if (previewFile) {
      await handleDownload(previewFile)
    }
  }

  // Handle delete
  const handleDelete = async (docId: string) => {
    Modal.confirm({
      title: '确认删除',
      icon: <ExclamationCircleOutlined />,
      content: '确定要删除这个文件吗？此操作不可恢复。',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          setDeletingDocId(docId)
          await api.delete(`/api/documents/${docId}`)
          message.success('删除成功')
          onRefresh()
        } catch (error) {
          message.error('删除失败')
        } finally {
          setDeletingDocId(null)
        }
      },
    })
  }

  // Render document actions
  const renderDocumentActions = (doc: DetailedDocumentInfo, docType: DetailedDocumentTypeInfo) => {
    const actions = []

    // Preview button
    actions.push(
      <Button
        key="preview"
        size="small"
        icon={<EyeOutlined />}
        onClick={() => handlePreview(doc, docType.documents)}
      >
        预览
      </Button>
    )

    // Download button
    actions.push(
      <Button
        key="download"
        size="small"
        icon={<DownloadOutlined />}
        onClick={() => handleDownload(doc)}
      >
        下载
      </Button>
    )

    // Delete button (only for rejected or pending)
    if (doc.status === 'rejected' || doc.status === 'pending') {
      actions.push(
        <Button
          key="delete"
          size="small"
          danger
          icon={<DeleteOutlined />}
          loading={deletingDocId === doc.id}
          onClick={() => handleDelete(doc.id)}
        >
          删除
        </Button>
      )
    }

    return actions
  }

  // Render document type card
  const renderDocumentTypeCard = (docType: DetailedDocumentTypeInfo) => {
    const hasDocuments = docType.documents.length > 0
    const isSatisfied = docType.is_required
      ? docType.approved_count >= docType.min_files
      : true

    return (
      <Card
        key={docType.id}
        size="small"
        style={{ marginBottom: 16 }}
        title={
          <Space>
            <Text strong>{docType.name}</Text>
            {docType.is_required ? (
              <Tag color="red">必填</Tag>
            ) : (
              <Tag>可选</Tag>
            )}
            <Tag color={getStatusColor(docType.upload_status)}>
              {getStatusText(docType.upload_status)}
            </Tag>
          </Space>
        }
        extra={
          <Button
            size="small"
            type={hasDocuments ? 'default' : 'primary'}
            icon={<UploadOutlined />}
            onClick={() => onUpload(docType.id)}
          >
            {hasDocuments ? '重新上传' : '上传'}
          </Button>
        }
      >
        {/* Description */}
        {docType.description && (
          <Alert
            message={docType.description}
            type="info"
            showIcon
            style={{ marginBottom: 12 }}
          />
        )}

        {/* Requirements */}
        <Space direction="vertical" style={{ width: '100%', marginBottom: 12 }}>
          <Text type="secondary">
            文件要求：{docType.min_files === docType.max_files
              ? `${docType.min_files} 个文件`
              : `${docType.min_files}-${docType.max_files} 个文件`}
            ，单个文件不超过 {formatFileSize(docType.max_file_size)}
          </Text>
          <Text type="secondary">
            支持格式：{docType.allowed_file_types}
          </Text>
          <Text type="secondary">
            已上传：{docType.uploaded_count} 个文件
            {docType.approved_count > 0 && ` (${docType.approved_count} 个已通过)`}
            {docType.pending_count > 0 && ` (${docType.pending_count} 个待审核)`}
            {docType.rejected_count > 0 && ` (${docType.rejected_count} 个已拒绝)`}
          </Text>
        </Space>

        {/* Document list */}
        {hasDocuments && (
          <List
            size="small"
            dataSource={docType.documents}
            renderItem={(doc) => (
              <List.Item
                actions={renderDocumentActions(doc, docType)}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <Text>{doc.file_name}</Text>
                      <Tag color={getStatusColor(doc.status)}>
                        {getStatusText(doc.status)}
                      </Tag>
                    </Space>
                  }
                  description={
                    <Space direction="vertical" size={0}>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        大小：{formatFileSize(doc.file_size)} | 上传时间：{formatDate(doc.uploaded_at)}
                      </Text>
                      {doc.status === 'approved' && doc.reviewed_at && (
                        <Text type="success" style={{ fontSize: 12 }}>
                          审核通过时间：{formatDate(doc.reviewed_at)}
                        </Text>
                      )}
                      {doc.status === 'rejected' && (
                        <Text type="danger" style={{ fontSize: 12 }}>
                          拒绝原因：{doc.reject_reason || doc.review_note || '无'}
                        </Text>
                      )}
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        )}

        {/* No documents message */}
        {!hasDocuments && (
          <Alert
            message="尚未上传任何文件"
            type="warning"
            showIcon
          />
        )}
      </Card>
    )
  }

  // Separate required and optional document types
  const requiredDocTypes = completeness.document_types.filter(dt => dt.is_required)
  const optionalDocTypes = completeness.document_types.filter(dt => !dt.is_required)

  return (
    <div>
      {/* Progress Overview */}
      <Card title="资料完整性" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <Progress
              percent={progress}
              status={getProgressStatus()}
              strokeColor={{
                '0%': '#ff4d4f',
                '50%': '#faad14',
                '100%': '#52c41a',
              }}
            />
            <div style={{ marginTop: 8, textAlign: 'center' }}>
              <Text style={{ fontSize: 16, fontWeight: 500 }}>
                已完成 {completeness.approved_required} / {completeness.total_required} 项必填资料
              </Text>
            </div>
          </div>

          {progress === 100 ? (
            <Alert
              message="资料已齐全，可以提交审核"
              type="success"
              showIcon
              icon={<CheckCircleOutlined />}
            />
          ) : (
            <Alert
              message={`还需完成 ${completeness.total_required - completeness.approved_required} 项必填资料`}
              type="warning"
              showIcon
              icon={<ClockCircleOutlined />}
            />
          )}
        </Space>
      </Card>

      {/* Required Documents */}
      {requiredDocTypes.length > 0 && (
        <Card title="必填资料" style={{ marginBottom: 16 }}>
          {requiredDocTypes.map(renderDocumentTypeCard)}
        </Card>
      )}

      {/* Optional Documents */}
      {optionalDocTypes.length > 0 && (
        <Collapse
          defaultActiveKey={[]}
          style={{ marginBottom: 16 }}
        >
          <Panel header={`可选资料 (${optionalDocTypes.length} 项)`} key="optional">
            {optionalDocTypes.map(renderDocumentTypeCard)}
          </Panel>
        </Collapse>
      )}

      {/* File Preview Modal */}
      {previewFile && (
        <FilePreview
          visible={previewVisible}
          onClose={() => {
            setPreviewVisible(false)
            setPreviewFile(null)
            setPreviewFiles([])
            setPreviewFileUrl('')
          }}
          fileUrl={previewFileUrl}
          fileName={previewFile.file_name}
          fileType={previewFile.file_type}
          files={previewFiles.map(f => ({
            id: f.id,
            file_name: f.file_name,
            file_url: `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/download/${f.id}?inline=true`,
            file_type: f.file_type,
          }))}
          currentFileId={previewFile.id}
          onFileChange={handlePreviewFileChange}
          onDownload={handleDownloadFromPreview}
        />
      )}
    </div>
  )
}

export default DetailedCompletenessView

