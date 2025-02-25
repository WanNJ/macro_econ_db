import React, { useState } from 'react';
import { Input, Button, Card, Tabs, Spin, Alert, Typography, Divider } from 'antd';
import { SendOutlined, AreaChartOutlined, FileTextOutlined, TableOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Search } = Input;
const { TabPane } = Tabs;
const { Title, Paragraph } = Typography;

const QueryInterface = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const handleSearch = async (value) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/query/natural_language', { query: value });
      setResult(response.data);
    } catch (err) {
      console.error('查询错误:', err);
      setError('查询处理过程中出现错误，请稍后再试。');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="query-interface">
      <Title level={2}>自然语言查询</Title>
      <Paragraph>
        使用自然语言描述您想了解的宏观经济数据信息，系统会为您提供相关分析和可视化。
      </Paragraph>
      <Paragraph type="secondary">
        示例: "比较过去五年中国和美国的GDP增长率" 或 "显示日本2010年至今的CPI变化趋势"
      </Paragraph>
      
      <Search
        placeholder="输入您的查询..."
        enterButton={<Button type="primary" icon={<SendOutlined />}>查询</Button>}
        size="large"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onSearch={handleSearch}
        style={{ marginBottom: 20 }}
      />
      
      {loading && <Spin tip="正在处理您的查询..." style={{ display: 'block', marginBottom: 20 }} />}
      
      {error && (
        <Alert message="错误" description={error} type="error" showIcon closable style={{ marginBottom: 20 }} />
      )}
      
      {result && (
        <Card>
          <Tabs defaultActiveKey="visualization">
            <TabPane
              tab={
                <span>
                  <AreaChartOutlined />
                  数据可视化
                </span>
              }
              key="visualization"
            >
              <div 
                dangerouslySetInnerHTML={{ 
                  __html: result.analysis.visualization.plot_html 
                }} 
              />
            </TabPane>
            <TabPane
              tab={
                <span>
                  <FileTextOutlined />
                  分析报告
                </span>
              }
              key="report"
            >
              <Title level={3}>{result.report.title}</Title>
              <Divider />
              <Paragraph><strong>摘要：</strong> {result.report.summary}</Paragraph>
              <Divider />
              <Title level={4}>关键发现</Title>
              <ul>
                {result.report.key_findings.map((finding, index) => (
                  <li key={index}>{finding}</li>
                ))}
              </ul>
            </TabPane>
            <TabPane
              tab={
                <span>
                  <TableOutlined />
                  数据表格
                </span>
              }
              key="data"
            >
              {result.report.data_tables.map((table, index) => (
                <div key={index} style={{ marginBottom: 20 }}>
                  <Title level={4}>{table.title}</Title>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr>
                        {table.headers.map((header, i) => (
                          <th key={i} style={{ border: '1px solid #ddd', padding: 8, textAlign: 'left' }}>
                            {header}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {table.rows.map((row, i) => (
                        <tr key={i}>
                          {Object.values(row).map((cell, j) => (
                            <td key={j} style={{ border: '1px solid #ddd', padding: 8 }}>
                              {typeof cell === 'number' ? cell.toFixed(2) : String(cell)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
            </TabPane>
          </Tabs>
        </Card>
      )}
    </div>
  );
};

export default QueryInterface;