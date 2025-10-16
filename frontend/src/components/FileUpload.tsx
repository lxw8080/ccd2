import React, { useState } from 'react'
import { Upload, message, Progress } from 'antd'
import { InboxOutlined } from '@ant-design/icons'
import type { UploadProps } from 'antd'
import imageCompression from 'browser-image-compression'
import { api } from '../services/api'

const { Dragger } = Upload

interface FileUploadProps {
  customerId: string
  documentTypeId: string
  onSuccess?: () => void
  maxSize?: number // MB
  accept?: string
}

const FileUpload: React.FC<FileUploadProps> = ({
  customerId,
  documentTypeId,
  onSuccess,
  maxSize = 20,
  accept = 'image/*,.pdf,.doc,.docx',
}) => {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)

  const compressImage = async (file: File): Promise<File> => {
    if (!file.type.startsWith('image/')) {
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
      
      const compressedFile = await imageCompression(file, options)
      return compressedFile
    } catch (error) {
      console.error('图片压缩失败:', error)
      return file
    }
  }

  const uploadFile = async (file: File) => {
    setUploading(true)
    setProgress(0)

    try {
      // 1. 检查文件大小
      if (file.size > maxSize * 1024 * 1024) {
        message.error(`文件大小不能超过 ${maxSize}MB`)
        return false
      }

      // 2. 压缩图片
      const processedFile = await compressImage(file)
      setProgress(50)

      // 3. 上传文件
      const formData = new FormData()
      formData.append('file', processedFile)
      formData.append('customer_id', customerId)
      formData.append('document_type_id', documentTypeId)

      await api.post('/api/documents/upload', formData, {
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.floor((progressEvent.loaded / progressEvent.total) * 50) + 50
            setProgress(percent)
          }
        },
      })

      setProgress(100)
      message.success('文件上传成功')
      
      if (onSuccess) {
        onSuccess()
      }

      // 重置进度
      setTimeout(() => {
        setProgress(0)
        setUploading(false)
      }, 1000)

      return false // 阻止默认上传行为
    } catch (error: any) {
      message.error(error.response?.data?.detail || '文件上传失败')
      setUploading(false)
      setProgress(0)
      return false
    }
  }

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept,
    beforeUpload: uploadFile,
    showUploadList: false,
    disabled: uploading,
  }

  return (
    <div>
      <Dragger {...uploadProps}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p className="ant-upload-hint">
          支持图片、PDF、Word文档，单个文件不超过 {maxSize}MB
        </p>
      </Dragger>
      {uploading && (
        <div style={{ marginTop: 16 }}>
          <Progress percent={progress} status="active" />
        </div>
      )}
    </div>
  )
}

export default FileUpload

