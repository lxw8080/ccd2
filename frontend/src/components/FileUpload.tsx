import React, { useState } from 'react'
import { Upload, message, Progress, Alert } from 'antd'
import { InboxOutlined } from '@ant-design/icons'
import type { UploadProps, UploadFile } from 'antd'
import imageCompression from 'browser-image-compression'
import { api } from '../services/api'
import type { DocumentType } from '../types'

const { Dragger } = Upload

interface FileUploadProps {
  customerId: string
  documentTypeId: string
  documentType?: DocumentType  // 资料类型配置
  onSuccess?: () => void
  maxSize?: number // MB (deprecated, use documentType.max_file_size instead)
  accept?: string  // (deprecated, use documentType.allowed_file_types instead)
}

const FileUpload: React.FC<FileUploadProps> = ({
  customerId,
  documentTypeId,
  documentType,
  onSuccess,
  maxSize = 20,
  accept = 'image/*,.pdf,.doc,.docx',
}) => {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [fileList, setFileList] = useState<UploadFile[]>([])

  // 从资料类型配置中获取限制
  const maxFileSize = documentType?.max_file_size
    ? documentType.max_file_size / 1024 / 1024  // 转换为 MB
    : maxSize
  const allowedTypes = documentType?.allowed_file_types || accept
  const minFiles = documentType?.min_files || 1
  const maxFiles = documentType?.max_files || 1
  const multiple = maxFiles > 1

  const compressImage = async (file: File): Promise<File> => {
    if (!file || !file.type || !file.type.startsWith('image/')) {
      return file
    }

    try {
      const options = {
        maxSizeMB: 1,
        maxWidthOrHeight: 1920,
        useWebWorker: true,
        onProgress: (percent: number) => {
          setProgress(Math.floor(percent / 2)) // 压缩占50%进度
        },
      }

      const compressedBlob = await imageCompression(file, options)

      // 确保压缩后的文件保留原始文件名和类型
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

  const validateFile = (file: File): boolean => {
    // 1. 检查文件大小
    if (file.size > maxFileSize * 1024 * 1024) {
      message.error(`文件 "${file.name}" 大小不能超过 ${maxFileSize}MB`)
      return false
    }

    // 2. 检查文件类型
    const fileExt = file.name.split('.').pop()?.toLowerCase()
    const allowedExtensions = allowedTypes.split(',').map(ext => ext.trim().toLowerCase().replace('.', ''))

    if (fileExt && !allowedExtensions.includes(fileExt)) {
      message.error(`文件 "${file.name}" 类型不支持。允许的类型：${allowedTypes}`)
      return false
    }

    return true
  }

  const uploadFiles = async () => {
    if (fileList.length === 0) {
      message.warning('请先选择文件')
      return
    }

    // 验证文件数量
    if (fileList.length < minFiles) {
      message.error(`至少需要上传 ${minFiles} 个文件`)
      return
    }

    if (fileList.length > maxFiles) {
      message.error(`最多只能上传 ${maxFiles} 个文件`)
      return
    }

    setUploading(true)
    setProgress(0)

    try {
      const formData = new FormData()
      formData.append('customer_id', customerId)
      formData.append('document_type_id', documentTypeId)

      // 处理每个文件
      for (let i = 0; i < fileList.length; i++) {
        // 获取原始文件对象
        const file = (fileList[i].originFileObj || fileList[i]) as File

        if (!file) {
          console.error('File object is undefined at index', i, fileList[i])
          continue
        }

        // 如果是图片，先压缩
        let processedFile = file
        if (file.type && file.type.startsWith('image/')) {
          processedFile = await compressImage(file)
          setProgress(Math.floor((i / fileList.length) * 30))
        }

        formData.append('files', processedFile)
      }

      // 上传所有文件
      await api.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.floor((progressEvent.loaded / progressEvent.total) * 70) + 30
            setProgress(percent)
          }
        },
      })

      setProgress(100)
      message.success(`成功上传 ${fileList.length} 个文件`)

      // 清空文件列表
      setFileList([])

      if (onSuccess) {
        onSuccess()
      }

      // 重置进度
      setTimeout(() => {
        setProgress(0)
        setUploading(false)
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
      setUploading(false)
      setProgress(0)
    }
  }

  const uploadProps: UploadProps = {
    name: 'files',
    multiple,
    accept: allowedTypes,
    fileList,
    beforeUpload: (file) => {
      if (!validateFile(file)) {
        return Upload.LIST_IGNORE
      }

      // 使用函数式更新来避免闭包问题
      setFileList((prevList) => {
        // 检查文件数量限制
        if (prevList.length >= maxFiles) {
          message.error(`最多只能上传 ${maxFiles} 个文件`)
          return prevList
        }

        // 创建符合 UploadFile 格式的对象
        const uploadFile = {
          uid: `${Date.now()}-${Math.random()}`,
          name: file.name,
          status: 'done' as const,
          originFileObj: file,
        }

        return [...prevList, uploadFile as any]
      })

      return false // 阻止自动上传
    },
    onRemove: (file) => {
      const index = fileList.indexOf(file)
      const newFileList = fileList.slice()
      newFileList.splice(index, 1)
      setFileList(newFileList)
    },
    disabled: uploading,
  }

  // 生成提示文本
  const getHintText = () => {
    const parts = []
    if (documentType) {
      parts.push(`支持格式：${documentType.allowed_file_types}`)
      parts.push(`单个文件不超过 ${maxFileSize}MB`)
      if (minFiles === maxFiles) {
        parts.push(`需要上传 ${minFiles} 个文件`)
      } else {
        parts.push(`需要上传 ${minFiles}-${maxFiles} 个文件`)
      }
    } else {
      parts.push(`支持图片、PDF、Word文档`)
      parts.push(`单个文件不超过 ${maxFileSize}MB`)
    }
    return parts.join('，')
  }

  return (
    <div>
      {documentType && documentType.description && (
        <Alert
          message={documentType.description}
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Dragger {...uploadProps}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">
          {multiple ? '点击或拖拽文件到此区域上传（可多选）' : '点击或拖拽文件到此区域上传'}
        </p>
        <p className="ant-upload-hint">
          {getHintText()}
        </p>
      </Dragger>

      {uploading && (
        <div style={{ marginTop: 16 }}>
          <Progress percent={progress} status="active" />
        </div>
      )}

      {!uploading && fileList.length > 0 && (
        <div style={{ marginTop: 16, textAlign: 'center' }}>
          <button
            onClick={uploadFiles}
            style={{
              padding: '8px 24px',
              backgroundColor: '#1890ff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            开始上传 ({fileList.length} 个文件)
          </button>
        </div>
      )}
    </div>
  )
}

export default FileUpload

