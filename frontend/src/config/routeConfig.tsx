/**
 * 路由配置文件
 * 支持动态路由和权限控制
 */
import { lazy, Suspense } from 'react'
import { Spin } from 'antd'
import { Navigate } from 'react-router-dom'

// 懒加载组件
const CustomerList = lazy(() => import('../pages/CustomerList'))
const CustomerDetail = lazy(() => import('../pages/CustomerDetail'))
const ProductList = lazy(() => import('../pages/ProductList'))
const DocumentTypeManagement = lazy(() => import('../pages/DocumentTypeManagement'))
const BatchImport = lazy(() => import('../pages/BatchImport'))
const DocumentManagement = lazy(() => import('../pages/DocumentManagement'))

// 加载中组件
const LoadingFallback = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
    <Spin size="large" />
  </div>
)

// 懒加载包装器
const LazyLoad = (Component: React.LazyExoticComponent<React.FC>) => (
  <Suspense fallback={<LoadingFallback />}>
    <Component />
  </Suspense>
)

export interface RouteConfig {
  path: string
  element: React.ReactNode
  roles?: string[] // 允许访问的角色列表
  children?: RouteConfig[]
}

/**
 * 路由配置
 * 支持嵌套路由和权限控制
 */
export const routeConfig: RouteConfig[] = [
  {
    path: '/',
    element: <Navigate to="/customers" replace />,
  },
  {
    path: '/customers',
    element: LazyLoad(CustomerList),
    roles: ['admin', 'customer_service', 'reviewer'],
  },
  {
    path: '/customers/:id',
    element: LazyLoad(CustomerDetail),
    roles: ['admin', 'customer_service', 'reviewer'],
  },
  {
    path: '/products',
    element: LazyLoad(ProductList),
    roles: ['admin'],
  },
  {
    path: '/document-types',
    element: LazyLoad(DocumentTypeManagement),
    roles: ['admin'],
  },
  {
    path: '/import',
    element: LazyLoad(BatchImport),
    roles: ['admin', 'customer_service'],
  },
  {
    path: '/documents',
    element: LazyLoad(DocumentManagement),
    roles: ['admin', 'customer_service', 'reviewer'],
  },
]

/**
 * 检查用户是否有权限访问路由
 * @param route 路由配置
 * @param userRole 用户角色
 * @returns 是否有权限
 */
export const hasRoutePermission = (route: RouteConfig, userRole?: string): boolean => {
  if (!userRole) return false
  if (!route.roles || route.roles.length === 0) return true
  return route.roles.includes(userRole)
}

/**
 * 根据用户角色过滤路由
 * @param routes 路由配置
 * @param userRole 用户角色
 * @returns 过滤后的路由
 */
export const filterRoutesByRole = (routes: RouteConfig[], userRole?: string): RouteConfig[] => {
  if (!userRole) return []

  return routes
    .filter(route => hasRoutePermission(route, userRole))
    .map(route => {
      if (route.children) {
        return {
          ...route,
          children: filterRoutesByRole(route.children, userRole),
        }
      }
      return route
    })
}

