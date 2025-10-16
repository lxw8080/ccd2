import React, { useState } from 'react'
import { Card, Upload, Button, Table, Alert, Space, Typography, Divider } from 'antd'
import { UploadOutlined, DownloadOutlined } from '@ant-design/icons'
import type { UploadProps } from 'antd'
import { api } from '../services/api'

const { Title, Paragraph } = Typography

interface ImportResult {
  success_count: number
  error_count: number
  errors: string[]
}

const BatchImport: React.FC = () => {
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<ImportResult | null>(null)

  const handleUpload: UploadProps['beforeUpload'] = async (file) => {
    setUploading(true)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post('/api/customers/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setResult(response.data)
    } catch (error: any) {
      setResult({
        success_count: 0,
        error_count: 1,
        errors: [error.response?.data?.detail || '导入失败'],
      })
    } finally {
      setUploading(false)
    }

    return false // 阻止默认上传
  }

  const downloadTemplate = () => {
    // 创建模板数据
    const template = [
      ['客户编号', '客户姓名', '手机号', '身份证号', '产品代码', '备注'],
      ['C001', '张三', '13800138000', '110101199001011234', 'personal_loan', '示例客户'],
      ['C002', '李四', '13900139000', '110101199002021234', 'car_loan', ''],
    ]

    // 转换为CSV
    const csv = template.map(row => row.join(',')).join('\n')
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = '客户导入模板.csv'
    link.click()
  }

  const errorColumns = [
    {
      title: '序号',
      dataIndex: 'index',
      key: 'index',
      width: 80,
      render: (_: any, __: any, index: number) => index + 1,
    },
    {
      title: '错误信息',
      dataIndex: 'error',
      key: 'error',
    },
  ]

  return (
    <div>
      <Title level={2}>批量导入客户</Title>

      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <Title level={4}>使用说明</Title>
            <Paragraph>
              1. 下载导入模板，按照模板格式填写客户信息
              <br />
              2. 支持Excel (.xlsx, .xls) 和 CSV (.csv) 格式
              <br />
              3. 必填字段：客户编号、客户姓名、产品代码
              <br />
              4. 产品代码需要与系统中已有的产品代码匹配
            </Paragraph>
            <Button icon={<DownloadOutlined />} onClick={downloadTemplate}>
              下载导入模板
            </Button>
          </div>

          <Divider />

          <div>
            <Title level={4}>上传文件</Title>
            <Upload
              beforeUpload={handleUpload}
              accept=".xlsx,.xls,.csv"
              showUploadList={false}
            >
              <Button
                type="primary"
                icon={<UploadOutlined />}
                loading={uploading}
                size="large"
              >
                {uploading ? '导入中...' : '选择文件并导入'}
              </Button>
            </Upload>
          </div>
        </Space>
      </Card>

      {result && (
        <Card title="导入结果">
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Alert
              message={`导入完成：成功 ${result.success_count} 条，失败 ${result.error_count} 条`}
              type={result.error_count === 0 ? 'success' : 'warning'}
              showIcon
            />

            {result.errors.length > 0 && (
              <div>
                <Title level={5}>错误详情</Title>
                <Table
                  columns={errorColumns}
                  dataSource={result.errors.map((error, index) => ({
                    key: index,
                    error,
                  }))}
                  pagination={false}
                  size="small"
                />
              </div>
            )}
          </Space>
        </Card>
      )}
    </div>
  )
}

export default BatchImport

