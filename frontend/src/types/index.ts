/**
 * 通用类型定义
 */

// 用户角色
export type UserRole = 'customer_service' | 'reviewer' | 'admin'

// 客户状态
export type CustomerStatus = 'collecting' | 'reviewing' | 'approved' | 'rejected'

// 文档状态
export type DocumentStatus = 'pending' | 'approved' | 'rejected'

// 上传来源
export type UploadSource = 'mobile' | 'pc' | 'scanner'

// 用户
export interface User {
  id: string
  username: string
  real_name?: string
  role: UserRole
  department?: string
  is_active: boolean
  created_at: string
}

// 贷款产品
export interface LoanProduct {
  id: string
  code: string
  name: string
  description?: string
  is_active: boolean
  created_at: string
}

// 资料类型
export interface DocumentType {
  id: string
  code: string
  name: string
  category?: string
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

// 产品资料要求
export interface ProductDocumentRequirement {
  id: string
  product_id: string
  document_type_id: string
  document_type?: DocumentType
  is_required: boolean
  min_files: number
  max_files: number
  sort_order: number
}

// 客户
export interface Customer {
  id: string
  customer_no: string
  name: string
  phone?: string
  id_card?: string
  product_id?: string
  product?: LoanProduct
  status: CustomerStatus
  created_at: string
  updated_at: string
}

// 客户资料文件
export interface CustomerDocument {
  id: string
  customer_id: string
  document_type_id: string
  document_type?: DocumentType
  file_name: string
  file_path: string
  file_size?: number
  file_type?: string
  uploaded_by: string
  uploader?: User
  upload_source?: UploadSource
  status: DocumentStatus
  reject_reason?: string
  created_at: string
}

// 完整性检查结果
export interface CompletenessResult {
  is_complete: boolean
  total_required: number
  total_completed: number
  missing_documents: Array<{
    id: string
    code: string
    name: string
    required: number
    uploaded: number
  }>
  insufficient_documents: Array<{
    id: string
    code: string
    name: string
    required: number
    uploaded: number
  }>
  completed_documents: Array<{
    id: string
    code: string
    name: string
    uploaded: number
  }>
  progress_percentage: number
}

// 分页参数
export interface PaginationParams {
  page: number
  page_size: number
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// API响应
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 详细完整性检查结果
export interface DetailedDocumentInfo {
  id: string
  file_name: string
  file_path: string
  file_size: number
  file_url: string
  status: 'pending' | 'approved' | 'rejected'
  uploaded_at: string | null
  reviewed_at: string | null
  review_note?: string
  reject_reason?: string
}

export interface DetailedDocumentTypeInfo {
  id: string
  code: string
  name: string
  category?: string
  description?: string
  is_required: boolean
  min_files: number
  max_files: number
  max_file_size: number
  allowed_file_types: string
  uploaded_count: number
  pending_count: number
  approved_count: number
  rejected_count: number
  upload_status: 'not_uploaded' | 'uploaded' | 'pending' | 'approved' | 'rejected'
  documents: DetailedDocumentInfo[]
}

export interface DetailedCompletenessResult {
  customer_id: string
  total_required: number
  uploaded_required: number
  approved_required: number
  document_types: DetailedDocumentTypeInfo[]
}
