import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  MessageOutlined,
  DatabaseOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';

const { Sider } = Layout;

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const handleMenuClick = (key) => {
    navigate(key);
  };
  
  // 根据当前路径确定选中的菜单项
  const selectedKey = location.pathname === '/' ? '/' : location.pathname;
  
  return (
    <Sider width={200} className="site-layout-background">
      <Menu
        mode="inline"
        selectedKeys={[selectedKey]}
        style={{ height: '100%', borderRight: 0 }}
        onClick={({ key }) => handleMenuClick(key)}
      >
        <Menu.Item key="/" icon={<DashboardOutlined />}>
          首页仪表盘
        </Menu.Item>
        <Menu.Item key="/query" icon={<MessageOutlined />}>
          自然语言查询
        </Menu.Item>
        <Menu.Item key="/data" icon={<DatabaseOutlined />}>
          数据浏览器
        </Menu.Item>
        <Menu.Item key="/about" icon={<InfoCircleOutlined />}>
          关于系统
        </Menu.Item>
      </Menu>
    </Sider>
  );
};

export default Sidebar;