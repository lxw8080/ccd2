import React from 'react'
import { Card, Timeline, Tag, Empty, Typography, Grid } from 'antd'
import { CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined } from '@ant-design/icons'
import type { DetailedCompletenessResult } from '../types'

const { Text } = Typography
const { useBreakpoint } = Grid

interface ReviewHistoryTabProps {
  completeness: DetailedCompletenessResult
}

const ReviewHistoryTab: React.FC<ReviewHistoryTabProps> = ({ completeness }) => {
  const screens = useBreakpoint()
  const isMobile = !screens.md
  // 收集所有文件的审核记录
  const reviewRecords: Array<{
    fileName: string
    documentTypeName: string
    status: string
    reviewedAt: string | null
    reviewNote: string | null
    uploadedAt: string
  }> = []

  completeness.document_types.forEach(docType => {
    docType.documents.forEach(doc => {
      if (doc.status !== 'pending') {
        reviewRecords.push({
          fileName: doc.file_name,
          documentTypeName: docType.name,
          status: doc.status,
          reviewedAt: doc.reviewed_at,
          reviewNote: doc.review_note,
          uploadedAt: doc.uploaded_at,
        })
      }
    })
  })

  // 按审核时间排序（最新的在前）
  reviewRecords.sort((a, b) => {
    const dateA = a.reviewedAt ? new Date(a.reviewedAt).getTime() : 0
    const dateB = b.reviewedAt ? new Date(b.reviewedAt).getTime() : 0
    return dateB - dateA
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      case 'rejected':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
      default:
        return <ClockCircleOutlined style={{ color: '#faad14' }} />
    }
  }

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'approved':
        return <Tag color="success">已通过</Tag>
      case 'rejected':
        return <Tag color="error">已拒绝</Tag>
      default:
        return <Tag color="processing">待审核</Tag>
    }
  }

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

  if (reviewRecords.length === 0) {
    return (
      <Card
        bordered={!isMobile}
        style={{
          marginLeft: isMobile ? -8 : 0,
          marginRight: isMobile ? -8 : 0,
          borderRadius: isMobile ? 0 : undefined
        }}
      >
        <Empty description="暂无审核记录" />
      </Card>
    )
  }

  return (
    <Card
      bordered={!isMobile}
      style={{
        marginLeft: isMobile ? -8 : 0,
        marginRight: isMobile ? -8 : 0,
        borderRadius: isMobile ? 0 : undefined
      }}
    >
      <Timeline mode={isMobile ? 'left' : undefined}>
        {reviewRecords.map((record, index) => (
          <Timeline.Item
            key={index}
            dot={getStatusIcon(record.status)}
          >
            <div>
              <div style={{ marginBottom: 8 }}>
                <Text strong style={{ fontSize: isMobile ? 14 : undefined }}>
                  {record.documentTypeName}
                </Text>
                {' - '}
                <Text
                  style={{
                    fontSize: isMobile ? 13 : undefined,
                    wordBreak: 'break-word'
                  }}
                >
                  {record.fileName}
                </Text>
                {' '}
                {getStatusTag(record.status)}
              </div>
              <div style={{ marginBottom: 4 }}>
                <Text type="secondary" style={{ fontSize: isMobile ? 12 : 12 }}>
                  上传时间：{formatDate(record.uploadedAt)}
                </Text>
              </div>
              {record.reviewedAt && (
                <div style={{ marginBottom: 4 }}>
                  <Text type="secondary" style={{ fontSize: isMobile ? 12 : 12 }}>
                    审核时间：{formatDate(record.reviewedAt)}
                  </Text>
                </div>
              )}
              {record.reviewNote && (
                <div>
                  <Text
                    type="secondary"
                    style={{
                      fontSize: isMobile ? 12 : 12,
                      wordBreak: 'break-word'
                    }}
                  >
                    审核意见：{record.reviewNote}
                  </Text>
                </div>
              )}
            </div>
          </Timeline.Item>
        ))}
      </Timeline>
    </Card>
  )
}

export default ReviewHistoryTab

