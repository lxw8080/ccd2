/**
 * 菜单配置文件
 * 支持动态菜单配置和权限控制
 */
import {
  TeamOutlined,
  FileTextOutlined,
  AppstoreOutlined,
  UploadOutlined,
  BarChartOutlined,
  SettingOutlined,
  AuditOutlined,
} from '@ant-design/icons'

export interface MenuItem {
  key: string
  path: string
  label: string
  icon?: any
  roles?: string[] // 允许访问的角色列表，为空表示所有角色都可访问
  children?: MenuItem[]
  hidden?: boolean // 是否隐藏
  badge?: number | string // 徽章数字
}

/**
 * 菜单配置
 * 可以根据需要动态调整菜单结构
 */
export const menuConfig: MenuItem[] = [
  {
    key: 'customers',
    path: '/customers',
    label: '客户管理',
    icon: TeamOutlined,
    roles: ['admin', 'customer_service', 'reviewer'],
  },
  {
    key: 'documents',
    path: '/documents',
    label: '资料管理',
    icon: FileTextOutlined,
    roles: ['admin', 'customer_service', 'reviewer'],
  },
  {
    key: 'products',
    path: '/products',
    label: '产品管理',
    icon: AppstoreOutlined,
    roles: ['admin'], // 仅管理员可访问
  },
  {
    key: 'document-types',
    path: '/document-types',
    label: '资料类型',
    icon: FileTextOutlined,
    roles: ['admin'], // 仅管理员可访问
  },
  {
    key: 'import',
    path: '/import',
    label: '批量导入',
    icon: UploadOutlined,
    roles: ['admin', 'customer_service'],
  },
  {
    key: 'reports',
    path: '/reports',
    label: '数据报表',
    icon: BarChartOutlined,
    roles: ['admin', 'reviewer'],
    hidden: true, // 暂时隐藏，未实现
  },
  {
    key: 'audit',
    path: '/audit',
    label: '审计日志',
    icon: AuditOutlined,
    roles: ['admin'],
    hidden: true, // 暂时隐藏，未实现
  },
  {
    key: 'settings',
    path: '/settings',
    label: '系统设置',
    icon: SettingOutlined,
    roles: ['admin'],
    hidden: true, // 暂时隐藏，未实现
  },
]

/**
 * 根据用户角色过滤菜单
 * @param menus 菜单配置
 * @param userRole 用户角色
 * @returns 过滤后的菜单
 */
export const filterMenuByRole = (menus: MenuItem[], userRole?: string): MenuItem[] => {
  if (!userRole) return []

  return menus
    .filter(menu => {
      // 过滤隐藏的菜单
      if (menu.hidden) return false
      
      // 如果没有指定角色，所有人都可以访问
      if (!menu.roles || menu.roles.length === 0) return true
      
      // 检查用户角色是否在允许的角色列表中
      return menu.roles.includes(userRole)
    })
    .map(menu => {
      // 递归过滤子菜单
      if (menu.children) {
        return {
          ...menu,
          children: filterMenuByRole(menu.children, userRole),
        }
      }
      return menu
    })
}

/**
 * 将菜单配置转换为 Ant Design Menu 组件所需的格式
 * @param menus 菜单配置
 * @returns Ant Design Menu items
 */
export const convertToAntdMenuItems = (menus: MenuItem[]) => {
  return menus.map(menu => {
    const Icon = menu.icon
    return {
      key: menu.path,
      icon: Icon ? <Icon /> : undefined,
      label: menu.label,
      children: menu.children ? convertToAntdMenuItems(menu.children) : undefined,
    }
  })
}

/**
 * 获取所有菜单路径
 * @param menus 菜单配置
 * @returns 路径列表
 */
export const getAllMenuPaths = (menus: MenuItem[]): string[] => {
  const paths: string[] = []
  
  const traverse = (items: MenuItem[]) => {
    items.forEach(item => {
      paths.push(item.path)
      if (item.children) {
        traverse(item.children)
      }
    })
  }
  
  traverse(menus)
  return paths
}

/**
 * 根据路径查找菜单项
 * @param menus 菜单配置
 * @param path 路径
 * @returns 菜单项
 */
export const findMenuByPath = (menus: MenuItem[], path: string): MenuItem | undefined => {
  for (const menu of menus) {
    if (menu.path === path) {
      return menu
    }
    if (menu.children) {
      const found = findMenuByPath(menu.children, path)
      if (found) return found
    }
  }
  return undefined
}

