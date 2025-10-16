import React, { useState } from 'react'
import { Card, Descriptions, Typography, Spin, Tabs, Modal, Select, Space, Button } from 'antd'
import { UploadOutlined, ArrowLeftOutlined } from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import type { Customer, CompletenessResult, CustomerDocument, DocumentType } from '../types'
import FileUpload from '../components/FileUpload'
import DocumentList from '../components/DocumentList'
import CompletenessIndicator from '../components/CompletenessIndicator'

const { Title } = Typography

const CustomerDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [uploadModalOpen, setUploadModalOpen] = useState(false)
  const [selectedDocType, setSelectedDocType] = useState<string>('')

  // Fetch customer
  const { data: customer, isLoading } = useQuery<Customer>({
    queryKey: ['customer', id],
    queryFn: async () => {
      const response = await api.get(`/api/customers/${id}`)
      return response.data
    },
  })

  // Fetch completeness
  const { data: completeness, refetch: refetchCompleteness } = useQuery<CompletenessResult>({
    queryKey: ['completeness', id],
    queryFn: async () => {
      const response = await api.get(`/api/documents/customer/${id}/completeness`)
      return response.data
    },
  })

  // Fetch documents
  const { data: documents, refetch: refetchDocuments } = useQuery<CustomerDocument[]>({
    queryKey: ['documents', id],
    queryFn: async () => {
      const response = await api.get(`/api/documents/customer/${id}`)
      return response.data
    },
  })

  // Fetch document types
  const { data: documentTypes } = useQuery<DocumentType[]>({
    queryKey: ['documentTypes'],
    queryFn: async () => {
      const response = await api.get('/api/products/document-types')
      return response.data
    },
  })

  const handleUploadSuccess = () => {
    setUploadModalOpen(false)
    setSelectedDocType('')
    refetchDocuments()
    refetchCompleteness()
  }

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/customers')}>
          返回
        </Button>
        <Title level={2} style={{ margin: 0 }}>客户详情</Title>
      </Space>

      <Card title="基本信息" style={{ marginBottom: 16 }}>
        <Descriptions column={2}>
          <Descriptions.Item label="客户编号">{customer?.customer_no}</Descriptions.Item>
          <Descriptions.Item label="客户姓名">{customer?.name}</Descriptions.Item>
          <Descriptions.Item label="手机号">{customer?.phone}</Descriptions.Item>
          <Descriptions.Item label="身份证号">{customer?.id_card}</Descriptions.Item>
          <Descriptions.Item label="贷款产品">{customer?.product?.name}</Descriptions.Item>
          <Descriptions.Item label="状态">{customer?.status}</Descriptions.Item>
          {customer?.note && (
            <Descriptions.Item label="备注" span={2}>{customer.note}</Descriptions.Item>
          )}
        </Descriptions>
      </Card>

      {completeness && <CompletenessIndicator completeness={completeness} />}

      <Card
        title="已上传资料"
        style={{ marginTop: 16 }}
        extra={
          <Button
            type="primary"
            icon={<UploadOutlined />}
            onClick={() => setUploadModalOpen(true)}
          >
            上传资料
          </Button>
        }
      >
        {documents && documents.length > 0 ? (
          <DocumentList
            documents={documents}
            customerId={id!}
            onDelete={() => {
              refetchDocuments()
              refetchCompleteness()
            }}
          />
        ) : (
          <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            暂无上传资料
          </div>
        )}
      </Card>

      <Modal
        title="上传资料"
        open={uploadModalOpen}
        onCancel={() => {
          setUploadModalOpen(false)
          setSelectedDocType('')
        }}
        footer={null}
        width={600}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <div style={{ marginBottom: 8 }}>选择资料类型：</div>
            <Select
              style={{ width: '100%' }}
              placeholder="请选择资料类型"
              value={selectedDocType || undefined}
              onChange={setSelectedDocType}
            >
              {documentTypes?.map((type) => (
                <Select.Option key={type.id} value={type.id}>
                  {type.name}
                </Select.Option>
              ))}
            </Select>
          </div>

          {selectedDocType && (
            <FileUpload
              customerId={id!}
              documentTypeId={selectedDocType}
              onSuccess={handleUploadSuccess}
            />
          )}
        </Space>
      </Modal>
    </div>
  )
}

export default CustomerDetail

