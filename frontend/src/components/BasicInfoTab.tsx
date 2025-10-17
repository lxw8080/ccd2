import React from 'react'
import { Card, Descriptions, Grid } from 'antd'
import type { Customer } from '../types'

const { useBreakpoint } = Grid

interface BasicInfoTabProps {
  customer: Customer
}

const BasicInfoTab: React.FC<BasicInfoTabProps> = ({ customer }) => {
  const screens = useBreakpoint()
  const isMobile = !screens.md

  return (
    <Card
      bordered={!isMobile}
      style={{
        marginLeft: isMobile ? -8 : 0,
        marginRight: isMobile ? -8 : 0,
        borderRadius: isMobile ? 0 : undefined
      }}
    >
      <Descriptions
        column={{ xs: 1, sm: 2, md: 2 }}
        bordered
        size={isMobile ? 'small' : 'default'}
        labelStyle={{
          fontWeight: 500,
          fontSize: isMobile ? 14 : undefined,
          padding: isMobile ? '8px 12px' : undefined
        }}
        contentStyle={{
          fontSize: isMobile ? 14 : undefined,
          padding: isMobile ? '8px 12px' : undefined,
          wordBreak: 'break-word'
        }}
      >
        <Descriptions.Item label="客户编号">{customer.customer_no}</Descriptions.Item>
        <Descriptions.Item label="客户姓名">{customer.name}</Descriptions.Item>
        <Descriptions.Item label="手机号">{customer.phone}</Descriptions.Item>
        <Descriptions.Item label="身份证号">{customer.id_card}</Descriptions.Item>
        <Descriptions.Item label="贷款产品">{customer.product?.name || '-'}</Descriptions.Item>
        <Descriptions.Item label="状态">{customer.status}</Descriptions.Item>
        {customer.note && (
          <Descriptions.Item label="备注" span={2}>{customer.note}</Descriptions.Item>
        )}
        <Descriptions.Item label="创建时间" span={2}>
          {new Date(customer.created_at).toLocaleString('zh-CN')}
        </Descriptions.Item>
      </Descriptions>
    </Card>
  )
}

export default BasicInfoTab

