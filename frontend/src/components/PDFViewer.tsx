import React, { useState } from 'react'
import { Document, Page } from 'react-pdf'
import { Button, Space, Spin, Alert } from 'antd'
import { ZoomInOutlined, ZoomOutOutlined, LeftOutlined, RightOutlined } from '@ant-design/icons'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'

// 导入 PDF.js 配置（使用本地 worker）
import '../config/pdfConfig'

interface PDFViewerProps {
  fileUrl: string
  fileName: string
  onLoadError?: (error: Error) => void
}

const PDFViewer: React.FC<PDFViewerProps> = ({ fileUrl, fileName, onLoadError }) => {
  const [numPages, setNumPages] = useState<number>(0)
  const [pageNumber, setPageNumber] = useState<number>(1)
  const [scale, setScale] = useState<number>(1.0)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string>('')

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
    setPageNumber(1)
    setLoading(false)
  }

  const onDocumentLoadError = (error: Error) => {
    console.error('PDF load error:', error)
    setError('PDF 加载失败，请尝试下载后查看')
    setLoading(false)
    if (onLoadError) {
      onLoadError(error)
    }
  }

  const changePage = (offset: number) => {
    setPageNumber(prevPageNumber => {
      const newPageNumber = prevPageNumber + offset
      if (newPageNumber < 1) return 1
      if (newPageNumber > numPages) return numPages
      return newPageNumber
    })
  }

  const previousPage = () => changePage(-1)
  const nextPage = () => changePage(1)

  const zoomIn = () => {
    setScale(prevScale => Math.min(prevScale + 0.2, 3.0))
  }

  const zoomOut = () => {
    setScale(prevScale => Math.max(prevScale - 0.2, 0.5))
  }

  if (error) {
    return (
      <Alert
        message="加载失败"
        description={error}
        type="error"
        showIcon
      />
    )
  }

  return (
    <div style={{ width: '100%', height: '100%' }}>
      {/* 控制栏 */}
      <div style={{ 
        padding: '10px', 
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: '#fafafa'
      }}>
        <Space>
          <Button
            icon={<LeftOutlined />}
            disabled={pageNumber <= 1}
            onClick={previousPage}
            size="small"
          >
            上一页
          </Button>
          <span style={{ margin: '0 10px' }}>
            第 {pageNumber} / {numPages} 页
          </span>
          <Button
            icon={<RightOutlined />}
            disabled={pageNumber >= numPages}
            onClick={nextPage}
            size="small"
          >
            下一页
          </Button>
        </Space>
        <Space>
          <Button
            icon={<ZoomOutOutlined />}
            onClick={zoomOut}
            disabled={scale <= 0.5}
            size="small"
          >
            缩小
          </Button>
          <span>{Math.round(scale * 100)}%</span>
          <Button
            icon={<ZoomInOutlined />}
            onClick={zoomIn}
            disabled={scale >= 3.0}
            size="small"
          >
            放大
          </Button>
        </Space>
      </div>

      {/* PDF 内容 */}
      <div style={{ 
        overflowY: 'auto', 
        height: 'calc(100vh - 300px)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'flex-start',
        padding: '20px',
        backgroundColor: '#525659'
      }}>
        {loading && (
          <div style={{ padding: '100px 0' }}>
            <Spin size="large" tip="加载 PDF..." />
          </div>
        )}
        <Document
          file={fileUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={onDocumentLoadError}
          loading={<Spin size="large" tip="加载 PDF..." />}
        >
          <Page
            pageNumber={pageNumber}
            scale={scale}
            renderTextLayer={true}
            renderAnnotationLayer={true}
            loading={<Spin size="large" />}
          />
        </Document>
      </div>
    </div>
  )
}

export default PDFViewer

