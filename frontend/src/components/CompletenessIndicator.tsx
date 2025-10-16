import React from 'react'
import { Card, Progress, List, Tag, Space } from 'antd'
import { CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons'
import type { CompletenessResult } from '../types'

interface CompletenessIndicatorProps {
  completeness: CompletenessResult
}

const CompletenessIndicator: React.FC<CompletenessIndicatorProps> = ({ completeness }) => {
  const getProgressStatus = () => {
    if (completeness.is_complete) return 'success'
    if (completeness.completion_percentage >= 50) return 'active'
    return 'exception'
  }

  return (
    <Card title="资料完整性" bordered={false}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 进度条 */}
        <div>
          <Progress
            percent={completeness.completion_percentage}
            status={getProgressStatus()}
            strokeColor={{
              '0%': '#108ee9',
              '100%': '#87d068',
            }}
          />
          <div style={{ marginTop: 8, textAlign: 'center' }}>
            <span style={{ fontSize: 16, fontWeight: 500 }}>
              已完成 {completeness.satisfied_requirements} / {completeness.total_requirements} 项
            </span>
          </div>
        </div>

        {/* 资料清单 */}
        <List
          size="small"
          dataSource={completeness.requirements}
          renderItem={(requirement) => (
            <List.Item
              extra={
                <Space>
                  <span>
                    {requirement.uploaded_count} / {requirement.min_files}
                  </span>
                  {requirement.is_satisfied ? (
                    <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 18 }} />
                  ) : (
                    <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: 18 }} />
                  )}
                </Space>
              }
            >
              <List.Item.Meta
                title={
                  <Space>
                    {requirement.document_type_name}
                    {requirement.is_required ? (
                      <Tag color="red">必需</Tag>
                    ) : (
                      <Tag>可选</Tag>
                    )}
                  </Space>
                }
                description={
                  requirement.is_satisfied
                    ? '已满足要求'
                    : `还需上传 ${requirement.min_files - requirement.uploaded_count} 个文件`
                }
              />
            </List.Item>
          )}
        />

        {/* 完成状态提示 */}
        {completeness.is_complete ? (
          <div
            style={{
              padding: 16,
              background: '#f6ffed',
              border: '1px solid #b7eb8f',
              borderRadius: 4,
              textAlign: 'center',
            }}
          >
            <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 24, marginRight: 8 }} />
            <span style={{ fontSize: 16, color: '#52c41a', fontWeight: 500 }}>
              资料已齐全，可以提交审核
            </span>
          </div>
        ) : (
          <div
            style={{
              padding: 16,
              background: '#fff7e6',
              border: '1px solid #ffd591',
              borderRadius: 4,
              textAlign: 'center',
            }}
          >
            <CloseCircleOutlined style={{ color: '#fa8c16', fontSize: 24, marginRight: 8 }} />
            <span style={{ fontSize: 16, color: '#fa8c16', fontWeight: 500 }}>
              资料尚未齐全，请继续上传
            </span>
          </div>
        )}
      </Space>
    </Card>
  )
}

export default CompletenessIndicator

