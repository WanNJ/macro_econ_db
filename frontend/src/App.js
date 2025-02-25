import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import AppHeader from './components/AppHeader';
import Sidebar from './components/Sidebar';
import Dashboard from './views/Dashboard';
import QueryInterface from './views/QueryInterface';
import DataExplorer from './views/DataExplorer';
import About from './views/About';
import './App.css';

const { Content } = Layout;

function App() {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <AppHeader />
        <Layout>
          <Sidebar />
          <Layout style={{ padding: '24px' }}>
            <Content
              style={{
                background: '#fff',
                padding: 24,
                margin: 0,
                minHeight: 280,
                borderRadius: '4px'
              }}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/query" element={<QueryInterface />} />
                <Route path="/data" element={<DataExplorer />} />
                <Route path="/about" element={<About />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Layout>
    </Router>
  );
}

export default App;