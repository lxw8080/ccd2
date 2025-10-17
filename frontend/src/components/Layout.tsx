import React, { useState, useMemo } from 'react'
import { Layout as AntLayout, Menu, Dropdown, Avatar, Space, Typography, Drawer, Button, Grid } from 'antd'
import {
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  MenuOutlined,
} from '@ant-design/icons'
import { useNavigate, useLocation, Outlet } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { menuConfig, filterMenuByRole, convertToAntdMenuItems } from '../config/menuConfig.tsx'

const { Header, Sider, Content } = AntLayout
const { Text } = Typography
const { useBreakpoint } = Grid

const Layout: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, clearAuth } = useAuthStore()
  const screens = useBreakpoint()
  const [drawerVisible, setDrawerVisible] = useState(false)

  // 判断是否为移动端
  const isMobile = !screens.md

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  const userMenu = (
    <Menu>
      <Menu.Item key="profile" icon={<UserOutlined />}>
        个人信息
      </Menu.Item>
      <Menu.Item key="settings" icon={<SettingOutlined />}>
        设置
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
        退出登录
      </Menu.Item>
    </Menu>
  )

  // 根据用户角色过滤菜单
  const filteredMenus = useMemo(() => {
    return filterMenuByRole(menuConfig, user?.role)
  }, [user?.role])

  // 转换为 Ant Design Menu 组件所需的格式
  const menuItems = useMemo(() => {
    return convertToAntdMenuItems(filteredMenus)
  }, [filteredMenus])

  const handleMenuClick = (key: string) => {
    navigate(key)
    if (isMobile) {
      setDrawerVisible(false)
    }
  }

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: isMobile ? '0 16px' : '0 24px'
      }}>
        <Space>
          {isMobile && (
            <Button
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setDrawerVisible(true)}
              style={{ color: 'white' }}
            />
          )}
          <div style={{
            color: 'white',
            fontSize: isMobile ? '16px' : '20px',
            fontWeight: 'bold'
          }}>
            {isMobile ? '资料收集' : '客户资料收集系统'}
          </div>
        </Space>
        <Dropdown overlay={userMenu} placement="bottomRight">
          <Space style={{ cursor: 'pointer' }}>
            <Avatar icon={<UserOutlined />} size={isMobile ? 'small' : 'default'} />
            {!isMobile && (
              <Text style={{ color: 'white' }}>{user?.full_name || user?.username}</Text>
            )}
          </Space>
        </Dropdown>
      </Header>

      <AntLayout>
        {/* 桌面端侧边栏 */}
        {!isMobile && (
          <Sider width={200} theme="light">
            <Menu
              mode="inline"
              selectedKeys={[location.pathname]}
              style={{ height: '100%', borderRight: 0 }}
              items={menuItems}
              onClick={({ key }) => handleMenuClick(key)}
            />
          </Sider>
        )}

        {/* 移动端抽屉菜单 */}
        {isMobile && (
          <Drawer
            title="菜单"
            placement="left"
            onClose={() => setDrawerVisible(false)}
            open={drawerVisible}
            bodyStyle={{ padding: 0 }}
          >
            <Menu
              mode="inline"
              selectedKeys={[location.pathname]}
              items={menuItems}
              onClick={({ key }) => handleMenuClick(key)}
            />
          </Drawer>
        )}

        <AntLayout style={{ padding: isMobile ? '12px' : '24px' }}>
          <Content
            style={{
              padding: isMobile ? 16 : 24,
              margin: 0,
              minHeight: 280,
              background: '#fff',
              borderRadius: '8px',
            }}
          >
            <Outlet />
          </Content>
        </AntLayout>
      </AntLayout>
    </AntLayout>
  )
}

export default Layout

