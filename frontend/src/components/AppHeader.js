import React from 'react';
import { Layout, Typography } from 'antd';

const { Header } = Layout;
const { Title } = Typography;

const AppHeader = () => {
  return (
    <Header className="header" style={{ display: 'flex', alignItems: 'center' }}>
      <div className="logo" />
      <Title level={3} style={{ margin: 0, color: 'white' }}>
        宏观经济数据智能系统
      </Title>
    </Header>
  );
};

export default AppHeader;