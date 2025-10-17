import React, { useState } from 'react'
import { Table, Button, Input, Space, Tag, message, Modal, Form, Select, Card, List, Grid, Row, Col } from 'antd'
import { PlusOutlined, SearchOutlined, EyeOutlined, PhoneOutlined, IdcardOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import type { Customer, LoanProduct, PaginatedResponse } from '../types'

const { Search } = Input
const { useBreakpoint } = Grid

const CustomerList: React.FC = () => {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const screens = useBreakpoint()

  // 判断是否为移动端
  const isMobile = !screens.md

  // Fetch customers
  const { data, isLoading } = useQuery<PaginatedResponse<Customer>>({
    queryKey: ['customers', page, pageSize, search],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      })
      if (search) params.append('search', search)

      const response = await api.get(`/api/customers/?${params}`)
      return response.data
    },
  })

  // Fetch products for form
  const { data: productsData } = useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const response = await api.get('/api/products/')
      return response.data
    },
  })

  // Extract items from paginated response
  const products = productsData?.items || []

  // Create customer mutation
  const createMutation = useMutation({
    mutationFn: async (values: any) => {
      const response = await api.post('/api/customers/', values)
      return response.data
    },
    onSuccess: () => {
      message.success('客户创建成功')
      setIsModalOpen(false)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['customers'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '创建失败')
    },
  })

  const columns = [
    {
      title: '客户编号',
      dataIndex: 'customer_no',
      key: 'customer_no',
      width: 150,
    },
    {
      title: '客户姓名',
      dataIndex: 'name',
      key: 'name',
      width: 120,
    },
    {
      title: '手机号',
      dataIndex: 'phone',
      key: 'phone',
      width: 130,
    },
    {
      title: '产品',
      dataIndex: ['product', 'name'],
      key: 'product',
      width: 150,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          pending: 'default',
          in_progress: 'processing',
          completed: 'success',
          rejected: 'error',
        }
        const textMap: Record<string, string> = {
          pending: '待处理',
          in_progress: '进行中',
          completed: '已完成',
          rejected: '已拒绝',
        }
        return <Tag color={colorMap[status]}>{textMap[status] || status}</Tag>
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: any, record: Customer) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => navigate(`/customers/${record.id}`)}
        >
          查看
        </Button>
      ),
    },
  ]

  const handleCreate = () => {
    form.validateFields().then(values => {
      createMutation.mutate(values)
    })
  }

  const getStatusTag = (status: string) => {
    const colorMap: Record<string, string> = {
      pending: 'default',
      collecting: 'processing',
      completed: 'success',
      rejected: 'error',
    }
    const textMap: Record<string, string> = {
      pending: '待处理',
      collecting: '收集中',
      completed: '已完成',
      rejected: '已拒绝',
    }
    return <Tag color={colorMap[status]}>{textMap[status] || status}</Tag>
  }

  return (
    <div>
      <div style={{
        marginBottom: 16,
        display: 'flex',
        flexDirection: isMobile ? 'column' : 'row',
        gap: isMobile ? 12 : 0,
        justifyContent: 'space-between'
      }}>
        <Search
          placeholder="搜索客户编号、姓名、手机号"
          allowClear
          style={{ width: isMobile ? '100%' : 300 }}
          onSearch={setSearch}
        />
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setIsModalOpen(true)}
          block={isMobile}
        >
          新建客户
        </Button>
      </div>

      {/* 桌面端表格视图 */}
      {!isMobile && (
        <Table
          columns={columns}
          dataSource={data?.items || []}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: data?.total || 0,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setPage(page)
              setPageSize(pageSize)
            },
          }}
        />
      )}

      {/* 移动端卡片视图 */}
      {isMobile && (
        <List
          loading={isLoading}
          dataSource={data?.items || []}
          renderItem={(customer: Customer) => (
            <Card
              style={{ marginBottom: 12 }}
              onClick={() => navigate(`/customers/${customer.id}`)}
            >
              <Row gutter={[8, 8]}>
                <Col span={24}>
                  <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                    <strong>{customer.name}</strong>
                    {getStatusTag(customer.status)}
                  </Space>
                </Col>
                <Col span={24}>
                  <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    <div>
                      <IdcardOutlined /> {customer.customer_no}
                    </div>
                    <div>
                      <PhoneOutlined /> {customer.phone || '未填写'}
                    </div>
                    <div>
                      产品: {customer.product?.name || '未选择'}
                    </div>
                  </Space>
                </Col>
              </Row>
            </Card>
          )}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: data?.total || 0,
            onChange: (page, pageSize) => {
              setPage(page)
              setPageSize(pageSize)
            },
            showSizeChanger: false,
            simple: true,
          }}
        />
      )}

      <Modal
        title="新建客户"
        open={isModalOpen}
        onOk={handleCreate}
        onCancel={() => {
          setIsModalOpen(false)
          form.resetFields()
        }}
        confirmLoading={createMutation.isPending}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="customer_no"
            label="客户编号"
            rules={[{ required: true, message: '请输入客户编号' }]}
          >
            <Input placeholder="请输入客户编号" />
          </Form.Item>
          <Form.Item
            name="name"
            label="客户姓名"
            rules={[{ required: true, message: '请输入客户姓名' }]}
          >
            <Input placeholder="请输入客户姓名" />
          </Form.Item>
          <Form.Item name="phone" label="手机号">
            <Input placeholder="请输入手机号" />
          </Form.Item>
          <Form.Item name="id_card" label="身份证号">
            <Input placeholder="请输入身份证号" />
          </Form.Item>
          <Form.Item
            name="product_id"
            label="贷款产品"
            rules={[{ required: true, message: '请选择贷款产品' }]}
          >
            <Select placeholder="请选择贷款产品">
              {products?.map(product => (
                <Select.Option key={product.id} value={product.id}>
                  {product.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="note" label="备注">
            <Input.TextArea rows={3} placeholder="请输入备注" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default CustomerList

