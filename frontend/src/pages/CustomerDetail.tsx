import React from 'react'
import { Tabs, Typography, Spin, Space, Button, Grid } from 'antd'
import { ArrowLeftOutlined, UserOutlined, FileTextOutlined, HistoryOutlined } from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import type { Customer, DetailedCompletenessResult } from '../types'
import BasicInfoTab from '../components/BasicInfoTab'
import DocumentUploadTab from '../components/DocumentUploadTab'
import ReviewHistoryTab from '../components/ReviewHistoryTab'

const { Title } = Typography
const { useBreakpoint } = Grid

const CustomerDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const screens = useBreakpoint()
  const isMobile = !screens.md

  // Fetch customer
  const { data: customer, isLoading } = useQuery<Customer>({
    queryKey: ['customer', id],
    queryFn: async () => {
      const response = await api.get(`/api/customers/${id}`)
      return response.data
    },
  })

  // Fetch detailed completeness
  const { data: detailedCompleteness, refetch: refetchCompleteness } = useQuery<DetailedCompletenessResult>({
    queryKey: ['detailedCompleteness', id],
    queryFn: async () => {
      const response = await api.get(`/api/documents/customer/${id}/detailed-completeness`)
      return response.data
    },
  })

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  if (!customer) return <div>客户不存在</div>

  const tabItems = [
    {
      key: 'basic',
      label: isMobile ? (
        <span style={{ fontSize: 14 }}>
          <UserOutlined />
          {' 基本'}
        </span>
      ) : (
        <span>
          <UserOutlined />
          {' 基本信息'}
        </span>
      ),
      children: <BasicInfoTab customer={customer} />,
    },
    {
      key: 'documents',
      label: isMobile ? (
        <span style={{ fontSize: 14 }}>
          <FileTextOutlined />
          {' 资料'}
        </span>
      ) : (
        <span>
          <FileTextOutlined />
          {' 资料上传'}
        </span>
      ),
      children: detailedCompleteness ? (
        <DocumentUploadTab
          customerId={id!}
          completeness={detailedCompleteness}
          onRefresh={refetchCompleteness}
        />
      ) : (
        <Spin />
      ),
    },
    {
      key: 'history',
      label: isMobile ? (
        <span style={{ fontSize: 14 }}>
          <HistoryOutlined />
          {' 记录'}
        </span>
      ) : (
        <span>
          <HistoryOutlined />
          {' 审核记录'}
        </span>
      ),
      children: detailedCompleteness ? (
        <ReviewHistoryTab completeness={detailedCompleteness} />
      ) : (
        <Spin />
      ),
    },
  ]

  return (
    <div style={{ padding: isMobile ? '0' : undefined }}>
      <Space
        style={{
          marginBottom: isMobile ? 12 : 16,
          width: '100%',
          flexWrap: 'wrap'
        }}
        size={isMobile ? 'small' : 'middle'}
      >
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/customers')}
          size={isMobile ? 'middle' : 'large'}
          style={{ minWidth: isMobile ? 44 : undefined, minHeight: isMobile ? 44 : undefined }}
        >
          {isMobile ? '' : '返回'}
        </Button>
        <Title
          level={isMobile ? 4 : 2}
          style={{ margin: 0, fontSize: isMobile ? 18 : undefined }}
        >
          客户详情
        </Title>
      </Space>

      <Tabs
        defaultActiveKey="basic"
        items={tabItems}
        size={isMobile ? 'middle' : 'large'}
        style={{
          marginLeft: isMobile ? -8 : 0,
          marginRight: isMobile ? -8 : 0
        }}
      />
    </div>
  )
}

export default CustomerDetail

