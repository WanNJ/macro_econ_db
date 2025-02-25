import React, { useState, useEffect } from 'react';
import { Card, Select, DatePicker, Button, Table, Spin, Typography, Space } from 'antd';
import { BarChartOutlined, LineChartOutlined } from '@ant-design/icons';
import axios from 'axios';
import moment from 'moment';

const { Option } = Select;
const { RangePicker } = DatePicker;
const { Title, Paragraph } = Typography;

const DataExplorer = () => {
  const [countries, setCountries] = useState([]);
  const [indicators, setIndicators] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [selectedIndicator, setSelectedIndicator] = useState(null);
  const [dateRange, setDateRange] = useState([moment().subtract(10, 'years'), moment()]);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [loadingMeta, setLoadingMeta] = useState(true);
  
  // 加载国家和指标数据
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const [countriesRes, indicatorsRes] = await Promise.all([
          axios.get('/api/data/countries'),
          axios.get('/api/data/indicators')
        ]);
        setCountries(countriesRes.data);
        setIndicators(indicatorsRes.data);
      } catch (error) {
        console.error('加载元数据错误:', error);
      } finally {
        setLoadingMeta(false);
      }
    };
    
    fetchMetadata();
  }, []);
  
  const handleSearch = async () => {
    if (!selectedCountry || !selectedIndicator) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.get('/api/data/data_points', {
        params: {
          country_code: selectedCountry,
          indicator_code: selectedIndicator,
          start_date: dateRange[0].format('YYYY-MM-DD'),
          end_date: dateRange[1].format('YYYY-MM-DD')
        }
      });
      
      // 转换数据为表格格式
      const formattedData = response.data.map((item, index) => ({
        key: index,
        date: moment(item.date).format('YYYY-MM-DD'),
        value: item.value
      }));
      
      setData(formattedData);
    } catch (error) {
      console.error('获取数据错误:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const columns = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      sorter: (a, b) => moment(a.date).unix() - moment(b.date).unix()
    },
    {
      title: '数值',
      dataIndex: 'value',
      key: 'value',
      render: (text) => text.toFixed(2)
    }
  ];
  
  return (
    <div className="data-explorer">
      <Title level={2}>数据浏览器</Title>
      <Paragraph>
        选择国家、指标和时间范围来浏览宏观经济数据。
      </Paragraph>
      
      <Card style={{ marginBottom: 20 }}>
        <Space style={{ marginBottom: 16 }} wrap>
          <Select
            placeholder="选择国家"
            style={{ width: 200 }}
            loading={loadingMeta}
            onChange={setSelectedCountry}
          >
            {countries.map((country) => (
              <Option key={country.code} value={country.code}>
                {country.name}
              </Option>
            ))}
          </Select>
          
          <Select
            placeholder="选择指标"
            style={{ width: 250 }}
            loading={loadingMeta}
            onChange={setSelectedIndicator}
          >
            {indicators.map((indicator) => (
              <Option key={indicator.name} value={indicator.name}>
                {indicator.name} ({indicator.unit})
              </Option>
            ))}
          </Select>
          
          <RangePicker
            value={dateRange}
            onChange={setDateRange}
          />
          
          <Button type="primary" onClick={handleSearch} loading={loading}>
            搜索
          </Button>
        </Space>
        
        <Space>
          <Button icon={<LineChartOutlined />} disabled={data.length === 0}>
            折线图
          </Button>
          <Button icon={<BarChartOutlined />} disabled={data.length === 0}>
            柱状图
          </Button>
        </Space>
      </Card>
      
      {loading ? (
        <Spin tip="加载数据中..." />
      ) : (
        <Table
          columns={columns}
          dataSource={data}
          pagination={{ pageSize: 10 }}
          bordered
          summary={(pageData) => {
            if (pageData.length === 0) return null;
            
            const values = pageData.map((item) => item.value);
            const avg = values.reduce((a, b) => a + b, 0) / values.length;
            const min = Math.min(...values);
            const max = Math.max(...values);
            
            return (
              <>
                <Table.Summary.Row>
                  <Table.Summary.Cell index={0}>平均值</Table.Summary.Cell>
                  <Table.Summary.Cell index={1}>{avg.toFixed(2)}</Table.Summary.Cell>
                </Table.Summary.Row>
                <Table.Summary.Row>
                  <Table.Summary.Cell index={0}>最小值</Table.Summary.Cell>
                  <Table.Summary.Cell index={1}>{min.toFixed(2)}</Table.Summary.Cell>
                </Table.Summary.Row>
                <Table.Summary.Row>
                  <Table.Summary.Cell index={0}>最大值</Table.Summary.Cell>
                  <Table.Summary.Cell index={1}>{max.toFixed(2)}</Table.Summary.Cell>
                </Table.Summary.Row>
              </>
            );
          }}
        />
      )}
    </div>
  );
};

export default DataExplorer;