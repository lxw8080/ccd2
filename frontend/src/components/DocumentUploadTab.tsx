import React, { useState } from 'react'
import { Card, Progress, Tag, Button, Space, List, Typography, Grid, Collapse, Alert, Modal, message, Upload } from 'antd'
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  UploadOutlined,
  EyeOutlined,
  DeleteOutlined,
  DownloadOutlined,
  ExclamationCircleOutlined,
  InboxOutlined,
} from '@ant-design/icons'
import type { UploadProps, UploadFile } from 'antd'
import imageCompression from 'browser-image-compression'
import type { DetailedCompletenessResult, DetailedDocumentTypeInfo, DetailedDocumentInfo } from '../types'
import { api } from '../services/api'
import FilePreview from './FilePreview'

const { Title, Text } = Typography
const { Panel } = Collapse
const { useBreakpoint } = Grid
const { Dragger } = Upload

interface DocumentUploadTabProps {
  customerId: string
  completeness: DetailedCompletenessResult
  onRefresh: () => void
}

const DocumentUploadTab: React.FC<DocumentUploadTabProps> = ({
  customerId,
  completeness,
  onRefresh,
}) => {
  const screens = useBreakpoint()
  const isMobile = !screens.md
  const [deletingDocId, setDeletingDocId] = useState<string | null>(null)
  const [uploadingTypeId, setUploadingTypeId] = useState<string | null>(null)
  const [expandedTypes, setExpandedTypes] = useState<string[]>([])
  
  // 文件预览状态
  const [previewVisible, setPreviewVisible] = useState(false)
  const [previewFile, setPreviewFile] = useState<DetailedDocumentInfo | null>(null)
  const [previewFiles, setPreviewFiles] = useState<DetailedDocumentInfo[]>([])
  const [previewFileUrl, setPreviewFileUrl] = useState<string>('')

  // 上传状态
  const [fileListMap, setFileListMap] = useState<Record<string, UploadFile[]>>({})
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})

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

  // Toggle upload area
  const toggleUploadArea = (typeId: string) => {
    setExpandedTypes(prev => 
      prev.includes(typeId) 
        ? prev.filter(id => id !== typeId)
        : [...prev, typeId]
    )
  }

  // Compress image
  const compressImage = async (file: File, typeId: string): Promise<File> => {
    if (!file || !file.type || !file.type.startsWith('image/')) {
      return file
    }

    try {
      const options = {
        maxSizeMB: 1,
        maxWidthOrHeight: 1920,
        useWebWorker: true,
        onProgress: (percent: number) => {
          setUploadProgress(prev => ({
            ...prev,
            [typeId]: Math.floor(percent / 2)
          }))
        },
      }

      const compressedBlob = await imageCompression(file, options)

      const compressedFile = new File(
        [compressedBlob],
        file.name,
        {
          type: file.type || compressedBlob.type,
          lastModified: Date.now()
        }
      )

      return compressedFile
    } catch (error) {
      console.error('图片压缩失败:', error)
      return file
    }
  }

  // Handle upload
  const handleUpload = async (docType: DetailedDocumentTypeInfo) => {
    const fileList = fileListMap[docType.id] || []
    
    if (fileList.length === 0) {
      message.warning('请先选择文件')
      return
    }

    if (fileList.length < docType.min_files) {
      message.error(`至少需要上传 ${docType.min_files} 个文件`)
      return
    }

    if (fileList.length > docType.max_files) {
      message.error(`最多只能上传 ${docType.max_files} 个文件`)
      return
    }

    setUploadingTypeId(docType.id)
    setUploadProgress(prev => ({ ...prev, [docType.id]: 0 }))

    try {
      const formData = new FormData()
      formData.append('customer_id', customerId)
      formData.append('document_type_id', docType.id)

      for (let i = 0; i < fileList.length; i++) {
        const file = (fileList[i].originFileObj || fileList[i]) as File

        if (!file) {
          console.error('File object is undefined at index', i, fileList[i])
          continue
        }

        let processedFile = file
        if (file.type && file.type.startsWith('image/')) {
          processedFile = await compressImage(file, docType.id)
          setUploadProgress(prev => ({
            ...prev,
            [docType.id]: Math.floor((i / fileList.length) * 30)
          }))
        }

        formData.append('files', processedFile)
      }

      await api.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.floor((progressEvent.loaded / progressEvent.total) * 70) + 30
            setUploadProgress(prev => ({ ...prev, [docType.id]: percent }))
          }
        },
      })

      setUploadProgress(prev => ({ ...prev, [docType.id]: 100 }))
      message.success(`成功上传 ${fileList.length} 个文件`)

      // Clear file list
      setFileListMap(prev => ({ ...prev, [docType.id]: [] }))
      setExpandedTypes(prev => prev.filter(id => id !== docType.id))

      // Refresh data
      onRefresh()

      setTimeout(() => {
        setUploadProgress(prev => {
          const newProgress = { ...prev }
          delete newProgress[docType.id]
          return newProgress
        })
        setUploadingTypeId(null)
      }, 1000)
    } catch (error: any) {
      console.error('Upload error:', error)
      let errorMessage = '文件上传失败'

      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.message) {
        errorMessage = `上传失败: ${error.message}`
      }

      message.error(errorMessage)
      setUploadingTypeId(null)
      setUploadProgress(prev => {
        const newProgress = { ...prev }
        delete newProgress[docType.id]
        return newProgress
      })
    }
  }

  // Render document actions
  const renderDocumentActions = (doc: DetailedDocumentInfo, docType: DetailedDocumentTypeInfo) => {
    const actions = []

    actions.push(
      <Button
        key="preview"
        size="small"
        icon={<EyeOutlined />}
        onClick={() => handlePreview(doc, docType.documents)}
        style={{ minWidth: isMobile ? 44 : undefined, minHeight: isMobile ? 44 : undefined }}
      >
        {isMobile ? '' : '预览'}
      </Button>
    )

    actions.push(
      <Button
        key="download"
        size="small"
        icon={<DownloadOutlined />}
        onClick={() => handleDownload(doc)}
        style={{ minWidth: isMobile ? 44 : undefined, minHeight: isMobile ? 44 : undefined }}
      >
        {isMobile ? '' : '下载'}
      </Button>
    )

    if (doc.status === 'rejected' || doc.status === 'pending') {
      actions.push(
        <Button
          key="delete"
          size="small"
          danger
          icon={<DeleteOutlined />}
          loading={deletingDocId === doc.id}
          onClick={() => handleDelete(doc.id)}
          style={{ minWidth: isMobile ? 44 : undefined, minHeight: isMobile ? 44 : undefined }}
        >
          {isMobile ? '' : '删除'}
        </Button>
      )
    }

    return actions
  }

  // Render document type card
  const renderDocumentTypeCard = (docType: DetailedDocumentTypeInfo) => {
    const hasDocuments = docType.documents.length > 0
    const isExpanded = expandedTypes.includes(docType.id)
    const isUploading = uploadingTypeId === docType.id
    const progress = uploadProgress[docType.id] || 0
    const fileList = fileListMap[docType.id] || []

    const maxFileSize = docType.max_file_size / 1024 / 1024
    const allowedTypes = docType.allowed_file_types

    const uploadProps: UploadProps = {
      name: 'files',
      multiple: docType.max_files > 1,
      accept: allowedTypes,
      fileList,
      beforeUpload: (file) => {
        // Validate file size
        if (file.size > docType.max_file_size) {
          message.error(`文件 "${file.name}" 大小不能超过 ${maxFileSize}MB`)
          return Upload.LIST_IGNORE
        }

        // Validate file type
        const fileExt = file.name.split('.').pop()?.toLowerCase()
        const allowedExtensions = allowedTypes.split(',').map(ext => ext.trim().toLowerCase().replace('.', ''))

        if (fileExt && !allowedExtensions.includes(fileExt)) {
          message.error(`文件 "${file.name}" 类型不支持。允许的类型：${allowedTypes}`)
          return Upload.LIST_IGNORE
        }

        setFileListMap(prev => {
          const currentList = prev[docType.id] || []
          
          if (currentList.length >= docType.max_files) {
            message.error(`最多只能上传 ${docType.max_files} 个文件`)
            return prev
          }

          const uploadFile = {
            uid: `${Date.now()}-${Math.random()}`,
            name: file.name,
            status: 'done' as const,
            originFileObj: file,
          }

          return {
            ...prev,
            [docType.id]: [...currentList, uploadFile as any]
          }
        })

        return false
      },
      onRemove: (file) => {
        setFileListMap(prev => {
          const currentList = prev[docType.id] || []
          const index = currentList.indexOf(file)
          const newFileList = currentList.slice()
          newFileList.splice(index, 1)
          return {
            ...prev,
            [docType.id]: newFileList
          }
        })
      },
      disabled: isUploading,
    }

    return (
      <Card
        key={docType.id}
        size="small"
        style={{
          marginBottom: isMobile ? 12 : 16,
          marginLeft: isMobile ? -8 : 0,
          marginRight: isMobile ? -8 : 0,
          borderRadius: isMobile ? 0 : undefined
        }}
        title={
          <Space wrap size={isMobile ? 'small' : 'middle'}>
            <Text strong style={{ fontSize: isMobile ? 14 : undefined }}>{docType.name}</Text>
            {docType.is_required ? (
              <Tag color="red" style={{ fontSize: isMobile ? 12 : undefined }}>必填</Tag>
            ) : (
              <Tag style={{ fontSize: isMobile ? 12 : undefined }}>可选</Tag>
            )}
            <Tag color={getStatusColor(docType.upload_status)} style={{ fontSize: isMobile ? 12 : undefined }}>
              {getStatusText(docType.upload_status)}
            </Tag>
          </Space>
        }
        extra={
          <Button
            size="small"
            type={isExpanded ? 'default' : 'primary'}
            icon={<UploadOutlined />}
            onClick={() => toggleUploadArea(docType.id)}
            style={{
              minWidth: isMobile ? 44 : undefined,
              minHeight: isMobile ? 44 : undefined,
              fontSize: isMobile ? 12 : undefined
            }}
          >
            {isExpanded ? '收起' : (hasDocuments ? (isMobile ? '上传' : '重新上传') : '上传')}
          </Button>
        }
      >
        {/* Description */}
        {docType.description && (
          <Alert
            message={docType.description}
            type="info"
            showIcon
            style={{
              marginBottom: 12,
              fontSize: isMobile ? 13 : undefined
            }}
          />
        )}

        {/* Requirements */}
        <Space direction="vertical" style={{ width: '100%', marginBottom: 12 }} size="small">
          <Text type="secondary" style={{ fontSize: isMobile ? 13 : undefined }}>
            文件要求：{docType.min_files === docType.max_files
              ? `${docType.min_files} 个文件`
              : `${docType.min_files}-${docType.max_files} 个文件`}
            ，单个文件不超过 {formatFileSize(docType.max_file_size)}
          </Text>
          <Text type="secondary" style={{ fontSize: isMobile ? 13 : undefined }}>
            支持格式：{docType.allowed_file_types}
          </Text>
          <Text type="secondary" style={{ fontSize: isMobile ? 13 : undefined }}>
            已上传：{docType.uploaded_count} 个文件
            {docType.approved_count > 0 && ` (${docType.approved_count} 个已通过)`}
            {docType.pending_count > 0 && ` (${docType.pending_count} 个待审核)`}
            {docType.rejected_count > 0 && ` (${docType.rejected_count} 个已拒绝)`}
          </Text>
        </Space>

        {/* Upload Area */}
        {isExpanded && (
          <div style={{ marginBottom: 12 }}>
            <Dragger {...uploadProps} style={{ fontSize: isMobile ? 13 : undefined }}>
              <p className="ant-upload-drag-icon" style={{ fontSize: isMobile ? 36 : undefined }}>
                <InboxOutlined />
              </p>
              <p className="ant-upload-text" style={{ fontSize: isMobile ? 14 : undefined, padding: isMobile ? '0 8px' : undefined }}>
                {docType.max_files > 1 ? (isMobile ? '点击或拖拽上传（可多选）' : '点击或拖拽文件到此区域上传（可多选）') : (isMobile ? '点击或拖拽上传' : '点击或拖拽文件到此区域上传')}
              </p>
              <p className="ant-upload-hint" style={{ fontSize: isMobile ? 12 : undefined, padding: isMobile ? '0 8px' : undefined }}>
                支持格式：{docType.allowed_file_types}，单个文件不超过 {maxFileSize}MB
              </p>
            </Dragger>

            {isUploading && (
              <div style={{ marginTop: 16 }}>
                <Progress percent={progress} status="active" />
              </div>
            )}

            {!isUploading && fileList.length > 0 && (
              <div style={{ marginTop: 16, textAlign: 'center' }}>
                <Button
                  type="primary"
                  onClick={() => handleUpload(docType)}
                  size={isMobile ? 'middle' : 'large'}
                  style={{
                    minWidth: isMobile ? '100%' : undefined,
                    minHeight: isMobile ? 44 : undefined
                  }}
                >
                  开始上传 ({fileList.length} 个文件)
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Document list */}
        {hasDocuments && (
          <List
            size="small"
            dataSource={docType.documents}
            renderItem={(doc) => (
              <List.Item
                actions={renderDocumentActions(doc, docType)}
                style={{
                  padding: isMobile ? '12px 0' : undefined,
                  flexWrap: isMobile ? 'wrap' : undefined
                }}
              >
                <List.Item.Meta
                  style={{ marginBottom: isMobile ? 8 : 0, width: isMobile ? '100%' : undefined }}
                  title={
                    <Space wrap size="small">
                      <Text
                        style={{
                          fontSize: isMobile ? 14 : undefined,
                          wordBreak: 'break-word',
                          maxWidth: isMobile ? '200px' : undefined
                        }}
                        ellipsis={isMobile ? { tooltip: doc.file_name } : false}
                      >
                        {doc.file_name}
                      </Text>
                      <Tag color={getStatusColor(doc.status)} style={{ fontSize: isMobile ? 12 : undefined }}>
                        {getStatusText(doc.status)}
                      </Tag>
                    </Space>
                  }
                  description={
                    <Space direction="vertical" size={0}>
                      <Text type="secondary" style={{ fontSize: isMobile ? 12 : 12 }}>
                        大小：{formatFileSize(doc.file_size)} | 上传时间：{formatDate(doc.uploaded_at)}
                      </Text>
                      {doc.status === 'approved' && doc.reviewed_at && (
                        <Text type="success" style={{ fontSize: isMobile ? 12 : 12 }}>
                          审核通过时间：{formatDate(doc.reviewed_at)}
                        </Text>
                      )}
                      {doc.status === 'rejected' && (
                        <Text type="danger" style={{ fontSize: isMobile ? 12 : 12, wordBreak: 'break-word' }}>
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
        {!hasDocuments && !isExpanded && (
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
    <div style={{
      marginLeft: isMobile ? -8 : 0,
      marginRight: isMobile ? -8 : 0
    }}>
      {/* Progress Overview */}
      <Card
        style={{
          marginBottom: isMobile ? 12 : 16,
          borderRadius: isMobile ? 0 : undefined
        }}
        bordered={!isMobile}
      >
        <Space direction="vertical" style={{ width: '100%' }} size={isMobile ? 'middle' : 'large'}>
          <div>
            <Progress
              percent={progress}
              status={getProgressStatus()}
              strokeColor={{
                '0%': '#ff4d4f',
                '50%': '#faad14',
                '100%': '#52c41a',
              }}
              strokeWidth={isMobile ? 12 : undefined}
            />
            <div style={{ marginTop: 8, textAlign: 'center' }}>
              <Text style={{ fontSize: isMobile ? 14 : 16, fontWeight: 500 }}>
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
              style={{ fontSize: isMobile ? 13 : undefined }}
            />
          ) : (
            <Alert
              message={`还需完成 ${completeness.total_required - completeness.approved_required} 项必填资料`}
              type="warning"
              showIcon
              icon={<ClockCircleOutlined />}
              style={{ fontSize: isMobile ? 13 : undefined }}
            />
          )}
        </Space>
      </Card>

      {/* Required Documents */}
      {requiredDocTypes.length > 0 && (
        <div style={{ marginBottom: isMobile ? 12 : 16 }}>
          <Title
            level={5}
            style={{
              marginBottom: isMobile ? 12 : 16,
              fontSize: isMobile ? 16 : undefined,
              paddingLeft: isMobile ? 8 : 0
            }}
          >
            必填资料
          </Title>
          {requiredDocTypes.map(renderDocumentTypeCard)}
        </div>
      )}

      {/* Optional Documents */}
      {optionalDocTypes.length > 0 && (
        <Collapse
          defaultActiveKey={[]}
          style={{
            marginBottom: isMobile ? 12 : 16,
            borderRadius: isMobile ? 0 : undefined
          }}
        >
          <Panel
            header={`可选资料 (${optionalDocTypes.length} 项)`}
            key="optional"
            style={{ fontSize: isMobile ? 14 : undefined }}
          >
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

export default DocumentUploadTab

