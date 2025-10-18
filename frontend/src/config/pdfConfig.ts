import { pdfjs } from 'react-pdf'

// 配置 PDF.js worker 使用本地版本
// 这样可以避免依赖外部CDN，适合中国大陆网络环境
// worker文件已复制到 public/pdf-worker 目录
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf-worker/pdf.worker.min.mjs'

export default pdfjs

