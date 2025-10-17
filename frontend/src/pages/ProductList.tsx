import React, { useState } from 'react'
import { Table, Button, Tag, Modal, Form, Input, Switch, message } from 'antd'
import { PlusOutlined, EditOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import type { LoanProduct } from '../types'

const ProductList: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState<LoanProduct | null>(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  // Fetch products
  const { data: productsData, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const response = await api.get('/api/products/')
      return response.data
    },
  })

  // Extract items from paginated response
  const products = productsData?.items || []

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: async (values: any) => {
      if (editingProduct) {
        const response = await api.put(`/api/products/${editingProduct.id}/`, values)
        return response.data
      } else {
        const response = await api.post('/api/products/', values)
        return response.data
      }
    },
    onSuccess: () => {
      message.success(editingProduct ? '产品更新成功' : '产品创建成功')
      setIsModalOpen(false)
      setEditingProduct(null)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  const columns = [
    {
      title: '产品代码',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: '产品名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'success' : 'default'}>
          {isActive ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: LoanProduct) => (
        <Button
          type="link"
          icon={<EditOutlined />}
          onClick={() => {
            setEditingProduct(record)
            form.setFieldsValue(record)
            setIsModalOpen(true)
          }}
        >
          编辑
        </Button>
      ),
    },
  ]

  const handleSave = () => {
    form.validateFields().then(values => {
      saveMutation.mutate(values)
    })
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2>产品管理</h2>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setEditingProduct(null)
            form.resetFields()
            setIsModalOpen(true)
          }}
        >
          新建产品
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={products || []}
        rowKey="id"
        loading={isLoading}
      />

      <Modal
        title={editingProduct ? '编辑产品' : '新建产品'}
        open={isModalOpen}
        onOk={handleSave}
        onCancel={() => {
          setIsModalOpen(false)
          setEditingProduct(null)
          form.resetFields()
        }}
        confirmLoading={saveMutation.isPending}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="code"
            label="产品代码"
            rules={[{ required: true, message: '请输入产品代码' }]}
          >
            <Input placeholder="请输入产品代码" disabled={!!editingProduct} />
          </Form.Item>
          <Form.Item
            name="name"
            label="产品名称"
            rules={[{ required: true, message: '请输入产品名称' }]}
          >
            <Input placeholder="请输入产品名称" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} placeholder="请输入描述" />
          </Form.Item>
          <Form.Item name="is_active" label="启用" valuePropName="checked" initialValue={true}>
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ProductList

