import React, { useState } from 'react'
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  InputNumber,
  Tag,
  message,
  Popconfirm,
  Grid,
  List,
  Row,
  Col,
  Divider
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  FileTextOutlined
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'

const { Option } = Select
const { TextArea } = Input
const { useBreakpoint } = Grid

interface DocumentType {
  id: string
  code: string
  name: string
  category: string
  description?: string
  is_required: boolean
  allowed_file_types?: string
  max_file_size: number
  min_files: number
  max_files: number
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

const DocumentTypeManagement: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingType, setEditingType] = useState<DocumentType | null>(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()
  const screens = useBreakpoint()
  const isMobile = !screens.md

  // Fetch document types
  const { data: documentTypes, isLoading } = useQuery<DocumentType[]>({
    queryKey: ['documentTypes'],
    queryFn: async () => {
      const response = await api.get('/api/products/document-types')
      return response.data
    },
  })

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: async (values: any) => {
      if (editingType) {
        return api.put(`/api/products/document-types/${editingType.id}`, values)
      } else {
        return api.post('/api/products/document-types', values)
      }
    },
    onSuccess: () => {
      message.success(editingType ? '更新成功' : '创建成功')
      setIsModalOpen(false)
      setEditingType(null)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['documentTypes'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      return api.delete(`/api/products/document-types/${id}`)
    },
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['documentTypes'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败')
    },
  })

  const columns = [
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      sorter: (a: DocumentType, b: DocumentType) => a.sort_order - b.sort_order,
    },
    {
      title: '资料类型',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: DocumentType) => (
        <Space direction="vertical" size={0}>
          <strong>{text}</strong>
          <span style={{ fontSize: '12px', color: '#999' }}>{record.code}</span>
        </Space>
      ),
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      render: (category: string) => {
        const categoryMap: Record<string, { text: string; color: string }> = {
          identity: { text: '身份', color: 'blue' },
          financial: { text: '财务', color: 'green' },
          credit: { text: '征信', color: 'orange' },
          other: { text: '其他', color: 'default' },
        }
        const cat = categoryMap[category] || categoryMap.other
        return <Tag color={cat.color}>{cat.text}</Tag>
      },
    },
    {
      title: '必填',
      dataIndex: 'is_required',
      key: 'is_required',
      width: 80,
      render: (required: boolean) => (
        <Tag color={required ? 'red' : 'default'}>{required ? '必填' : '可选'}</Tag>
      ),
    },
    {
      title: '文件数量',
      key: 'files',
      width: 100,
      render: (_: any, record: DocumentType) => `${record.min_files}-${record.max_files}`,
    },
    {
      title: '文件大小',
      dataIndex: 'max_file_size',
      key: 'max_file_size',
      width: 100,
      render: (size: number) => `${(size / 1024 / 1024).toFixed(1)}MB`,
    },
    {
      title: '允许类型',
      dataIndex: 'allowed_file_types',
      key: 'allowed_file_types',
      width: 150,
      render: (types: string) => types || '全部',
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (active: boolean) => (
        <Tag color={active ? 'success' : 'default'}>{active ? '启用' : '禁用'}</Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right' as const,
      render: (_: any, record: DocumentType) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingType(record)
              form.setFieldsValue(record)
              setIsModalOpen(true)
            }}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此资料类型吗？"
            description="删除后无法恢复"
            onConfirm={() => deleteMutation.mutate(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const handleSave = () => {
    form.validateFields().then((values) => {
      saveMutation.mutate(values)
    })
  }

  // 移动端卡片渲染
  const renderMobileCard = (item: DocumentType) => {
    const categoryMap: Record<string, { text: string; color: string }> = {
      identity: { text: '身份', color: 'blue' },
      financial: { text: '财务', color: 'green' },
      credit: { text: '征信', color: 'orange' },
      other: { text: '其他', color: 'default' },
    }
    const cat = categoryMap[item.category] || categoryMap.other

    return (
      <Card
        key={item.id}
        size="small"
        style={{ marginBottom: 12 }}
        extra={
          <Space>
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              onClick={() => {
                setEditingType(item)
                form.setFieldsValue(item)
                setIsModalOpen(true)
              }}
            />
            <Popconfirm
              title="确定删除？"
              onConfirm={() => deleteMutation.mutate(item.id)}
            >
              <Button type="link" size="small" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Space>
        }
      >
        <Row gutter={[8, 8]}>
          <Col span={24}>
            <Space>
              <strong style={{ fontSize: 16 }}>{item.name}</strong>
              <Tag color={cat.color}>{cat.text}</Tag>
              <Tag color={item.is_required ? 'red' : 'default'}>
                {item.is_required ? '必填' : '可选'}
              </Tag>
              <Tag color={item.is_active ? 'success' : 'default'}>
                {item.is_active ? '启用' : '禁用'}
              </Tag>
            </Space>
          </Col>
          <Col span={24}>
            <span style={{ fontSize: 12, color: '#999' }}>代码: {item.code}</span>
          </Col>
          {item.description && (
            <Col span={24}>
              <span style={{ fontSize: 12 }}>{item.description}</span>
            </Col>
          )}
          <Col span={12}>
            <span style={{ fontSize: 12 }}>
              文件数量: {item.min_files}-{item.max_files}
            </span>
          </Col>
          <Col span={12}>
            <span style={{ fontSize: 12 }}>
              最大: {(item.max_file_size / 1024 / 1024).toFixed(1)}MB
            </span>
          </Col>
          <Col span={24}>
            <span style={{ fontSize: 12 }}>
              允许类型: {item.allowed_file_types || '全部'}
            </span>
          </Col>
        </Row>
      </Card>
    )
  }

  return (
    <div>
      <Card
        title={
          <Space>
            <FileTextOutlined />
            资料类型管理
          </Space>
        }
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditingType(null)
              form.resetFields()
              setIsModalOpen(true)
            }}
          >
            {isMobile ? '新建' : '新建资料类型'}
          </Button>
        }
      >
        {!isMobile ? (
          <Table
            columns={columns}
            dataSource={documentTypes || []}
            rowKey="id"
            loading={isLoading}
            scroll={{ x: 1200 }}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
          />
        ) : (
          <List
            dataSource={documentTypes || []}
            loading={isLoading}
            renderItem={renderMobileCard}
          />
        )}
      </Card>

      <Modal
        title={editingType ? '编辑资料类型' : '新建资料类型'}
        open={isModalOpen}
        onOk={handleSave}
        onCancel={() => {
          setIsModalOpen(false)
          setEditingType(null)
          form.resetFields()
        }}
        confirmLoading={saveMutation.isPending}
        width={isMobile ? '100%' : 720}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item
                name="code"
                label="资料代码"
                rules={[{ required: true, message: '请输入资料代码' }]}
              >
                <Input placeholder="如：id_card" disabled={!!editingType} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item
                name="name"
                label="资料名称"
                rules={[{ required: true, message: '请输入资料名称' }]}
              >
                <Input placeholder="如：身份证" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="category"
            label="分类"
            rules={[{ required: true, message: '请选择分类' }]}
          >
            <Select placeholder="请选择分类">
              <Option value="identity">身份证明</Option>
              <Option value="financial">财务资料</Option>
              <Option value="credit">征信资料</Option>
              <Option value="other">其他</Option>
            </Select>
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea rows={2} placeholder="资料类型描述" />
          </Form.Item>

          <Row gutter={16}>
            <Col xs={24} sm={8}>
              <Form.Item name="is_required" label="是否必填" valuePropName="checked">
                <Switch checkedChildren="必填" unCheckedChildren="可选" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item name="is_active" label="是否启用" valuePropName="checked" initialValue={true}>
                <Switch checkedChildren="启用" unCheckedChildren="禁用" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item name="sort_order" label="排序" initialValue={0}>
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="allowed_file_types"
            label="允许的文件类型"
            tooltip="多个类型用逗号分隔，如：jpg,png,pdf"
          >
            <Input placeholder="jpg,png,pdf,doc,docx,xls,xlsx" />
          </Form.Item>

          <Row gutter={16}>
            <Col xs={24} sm={8}>
              <Form.Item
                name="min_files"
                label="最少文件数"
                initialValue={1}
                rules={[{ required: true }]}
              >
                <InputNumber min={1} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item
                name="max_files"
                label="最多文件数"
                initialValue={1}
                rules={[{ required: true }]}
              >
                <InputNumber min={1} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item
                name="max_file_size"
                label="最大文件大小(MB)"
                initialValue={10}
                rules={[{ required: true }]}
              >
                <InputNumber
                  min={1}
                  max={100}
                  style={{ width: '100%' }}
                  formatter={(value) => `${value} MB`}
                  parser={(value) => value?.replace(' MB', '') as any}
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  )
}

export default DocumentTypeManagement

