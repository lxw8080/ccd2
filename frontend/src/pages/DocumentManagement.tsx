import React, { useState } from 'react'
import { Card, Table, Tag, Button, Space, Input, Select, Modal, message, List, Row, Col, Grid } from 'antd'
import { SearchOutlined, EyeOutlined, CheckOutlined, CloseOutlined, DownloadOutlined, FileOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import type { CustomerDocument } from '../types'

const { Search } = Input
const { Option } = Select
const { TextArea } = Input
const { useBreakpoint } = Grid

interface DocumentWithCustomer extends CustomerDocument {
  customer_name?: string
  customer_no?: string
  document_type_name?: string
}

const DocumentManagement: React.FC = () => {
  const queryClient = useQueryClient()
  const [searchText, setSearchText] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [reviewModalOpen, setReviewModalOpen] = useState(false)
  const [selectedDocument, setSelectedDocument] = useState<DocumentWithCustomer | null>(null)
  const [reviewStatus, setReviewStatus] = useState<'approved' | 'rejected'>('approved')
  const [reviewNote, setReviewNote] = useState('')
  const screens = useBreakpoint()

  // 判断是否为移动端
  const isMobile = !screens.md

  // Fetch all documents (we'll need to create this API endpoint)
  const { data: documents, isLoading } = useQuery<DocumentWithCustomer[]>({
    queryKey: ['all-documents', statusFilter],
    queryFn: async () => {
      // For now, we'll fetch customers and their documents
      // In a real app, you'd have a dedicated endpoint for all documents
      const customersResponse = await api.get('/api/customers/?page=1&page_size=100')
      const customers = customersResponse.data.items || []
      
      const allDocuments: DocumentWithCustomer[] = []
      
      for (const customer of customers) {
        try {
          const docsResponse = await api.get(`/api/documents/customer/${customer.id}`)
          const docs = docsResponse.data || []
          
          docs.forEach((doc: CustomerDocument) => {
            allDocuments.push({
              ...doc,
              customer_name: customer.name,
              customer_no: customer.customer_no,
            })
          })
        } catch (error) {
          console.error(`Failed to fetch documents for customer ${customer.id}`, error)
        }
      }
      
      return allDocuments
    },
  })

  // Review mutation
  const reviewMutation = useMutation({
    mutationFn: async ({ documentId, status, note }: { documentId: string; status: string; note?: string }) => {
      await api.post(`/api/documents/${documentId}/review`, {
        status,
        review_note: note,
      })
    },
    onSuccess: () => {
      message.success('审核成功')
      setReviewModalOpen(false)
      setSelectedDocument(null)
      setReviewNote('')
      queryClient.invalidateQueries({ queryKey: ['all-documents'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '审核失败')
    },
  })

  const handleReview = () => {
    if (!selectedDocument) return
    
    reviewMutation.mutate({
      documentId: selectedDocument.id,
      status: reviewStatus,
      note: reviewNote,
    })
  }

  const handleDownload = (document: DocumentWithCustomer) => {
    if (document.file_url) {
      window.open(document.file_url, '_blank')
    } else {
      message.warning('文件URL不可用')
    }
  }

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      pending: { color: 'orange', text: '待审核' },
      approved: { color: 'green', text: '已通过' },
      rejected: { color: 'red', text: '已拒绝' },
    }
    const config = statusMap[status] || { color: 'default', text: status }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const filteredDocuments = documents?.filter((doc) => {
    const matchesSearch = 
      doc.customer_name?.toLowerCase().includes(searchText.toLowerCase()) ||
      doc.customer_no?.toLowerCase().includes(searchText.toLowerCase()) ||
      doc.file_name?.toLowerCase().includes(searchText.toLowerCase())
    
    const matchesStatus = statusFilter === 'all' || doc.status === statusFilter
    
    return matchesSearch && matchesStatus
  })

  const columns = [
    {
      title: '客户编号',
      dataIndex: 'customer_no',
      key: 'customer_no',
      width: 120,
    },
    {
      title: '客户姓名',
      dataIndex: 'customer_name',
      key: 'customer_name',
      width: 120,
    },
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
      ellipsis: true,
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (size: number) => {
        if (size < 1024) return `${size} B`
        if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`
        return `${(size / (1024 * 1024)).toFixed(2)} MB`
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: any, record: DocumentWithCustomer) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(record)}
          >
            下载
          </Button>
          {record.status === 'pending' && (
            <Button
              type="link"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => {
                setSelectedDocument(record)
                setReviewModalOpen(true)
              }}
            >
              审核
            </Button>
          )}
        </Space>
      ),
    },
  ]

  const pendingCount = documents?.filter(doc => doc.status === 'pending').length || 0
  const approvedCount = documents?.filter(doc => doc.status === 'approved').length || 0
  const rejectedCount = documents?.filter(doc => doc.status === 'rejected').length || 0

  const formatFileSize = (size: number) => {
    if (size < 1024) return `${size} B`
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`
    return `${(size / (1024 * 1024)).toFixed(2)} MB`
  }

  return (
    <div>
      <Card
        title="资料管理"
        extra={
          isMobile ? null : (
            <Space>
              <Select
                value={statusFilter}
                onChange={setStatusFilter}
                style={{ width: 120 }}
              >
                <Option value="all">全部状态</Option>
                <Option value="pending">待审核 ({pendingCount})</Option>
                <Option value="approved">已通过 ({approvedCount})</Option>
                <Option value="rejected">已拒绝 ({rejectedCount})</Option>
              </Select>
              <Search
                placeholder="搜索客户编号、姓名或文件名"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                style={{ width: 300 }}
                allowClear
              />
            </Space>
          )
        }
      >
        {/* 移动端筛选器 */}
        {isMobile && (
          <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }} size={12}>
            <Select
              value={statusFilter}
              onChange={setStatusFilter}
              style={{ width: '100%' }}
            >
              <Option value="all">全部状态</Option>
              <Option value="pending">待审核 ({pendingCount})</Option>
              <Option value="approved">已通过 ({approvedCount})</Option>
              <Option value="rejected">已拒绝 ({rejectedCount})</Option>
            </Select>
            <Search
              placeholder="搜索客户编号、姓名或文件名"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              allowClear
            />
          </Space>
        )}

        {/* 桌面端表格视图 */}
        {!isMobile && (
          <Table
            columns={columns}
            dataSource={filteredDocuments}
            rowKey="id"
            loading={isLoading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
          />
        )}

        {/* 移动端列表视图 */}
        {isMobile && (
          <List
            loading={isLoading}
            dataSource={filteredDocuments}
            renderItem={(document: DocumentWithCustomer) => (
              <Card style={{ marginBottom: 12 }} size="small">
                <Row gutter={[8, 8]}>
                  <Col span={24}>
                    <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                      <Space>
                        <FileOutlined />
                        <strong>{document.file_name}</strong>
                      </Space>
                      {getStatusTag(document.status)}
                    </Space>
                  </Col>
                  <Col span={24}>
                    <Space direction="vertical" size={4} style={{ width: '100%', fontSize: '12px', color: '#666' }}>
                      <div>客户: {document.customer_name} ({document.customer_no})</div>
                      <div>大小: {formatFileSize(document.file_size)}</div>
                      <div>时间: {new Date(document.created_at).toLocaleString('zh-CN')}</div>
                    </Space>
                  </Col>
                  <Col span={24}>
                    <Space>
                      <Button
                        size="small"
                        icon={<DownloadOutlined />}
                        onClick={() => handleDownload(document)}
                      >
                        下载
                      </Button>
                      {document.status === 'pending' && (
                        <Button
                          size="small"
                          type="primary"
                          icon={<EyeOutlined />}
                          onClick={() => {
                            setSelectedDocument(document)
                            setReviewModalOpen(true)
                          }}
                        >
                          审核
                        </Button>
                      )}
                    </Space>
                  </Col>
                </Row>
              </Card>
            )}
            pagination={{
              pageSize: 10,
              showTotal: (total) => `共 ${total} 条`,
              simple: true,
            }}
          />
        )}
      </Card>

      <Modal
        title="审核资料"
        open={reviewModalOpen}
        onOk={handleReview}
        onCancel={() => {
          setReviewModalOpen(false)
          setSelectedDocument(null)
          setReviewNote('')
        }}
        confirmLoading={reviewMutation.isPending}
        okText="提交"
        cancelText="取消"
      >
        {selectedDocument && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div>
              <p><strong>客户:</strong> {selectedDocument.customer_name} ({selectedDocument.customer_no})</p>
              <p><strong>文件名:</strong> {selectedDocument.file_name}</p>
              <p><strong>上传时间:</strong> {new Date(selectedDocument.created_at).toLocaleString('zh-CN')}</p>
            </div>
            
            <div>
              <p><strong>审核结果:</strong></p>
              <Space>
                <Button
                  type={reviewStatus === 'approved' ? 'primary' : 'default'}
                  icon={<CheckOutlined />}
                  onClick={() => setReviewStatus('approved')}
                >
                  通过
                </Button>
                <Button
                  type={reviewStatus === 'rejected' ? 'primary' : 'default'}
                  danger={reviewStatus === 'rejected'}
                  icon={<CloseOutlined />}
                  onClick={() => setReviewStatus('rejected')}
                >
                  拒绝
                </Button>
              </Space>
            </div>

            <div>
              <p><strong>审核意见:</strong></p>
              <TextArea
                rows={4}
                value={reviewNote}
                onChange={(e) => setReviewNote(e.target.value)}
                placeholder="请输入审核意见（选填）"
              />
            </div>
          </Space>
        )}
      </Modal>
    </div>
  )
}

export default DocumentManagement

