import { Form, Input, Select, Space, Button, Layout, Row, Col } from 'antd';
import { LinkOutlined } from '@ant-design/icons'
import { useForm } from 'antd/lib/form/Form';
import { Link } from 'react-router-dom';
import { Site } from './types';

const { Content, Sider } = Layout

export function SiteForm(props: {
  onFinish: (user: Partial<Site>) => void;
  initialValues?: Site;
}) {
  const [form] = useForm();

  const scrapes = [
    { value: 'SimpleDocumentScrape', label: 'Simple Document Scrape' },
    { value: 'BrowserDocumentScrape', label: 'Browser Document Scrape' },
    { value: 'MyPrimeSearchableScrape', label: 'MyPrime Searchable Scrape' },
  ];

  const schedules = [
    { value: '0 16 * * *', label: 'Daily' },
    { value: '0 16 * * 0', label: 'Weekly' },
    { value: '0 16 1 * *', label: 'Monthly' },
  ];

  const validateMessages = {
    required: '${label} is required!',
    types: {
      url: "${label} is not a valid url!"
    }
  }

  return (
    <Form
      layout="vertical"
      form={form}
      wrapperCol={{ span: 7 }}
      requiredMark={false}
      onFinish={props.onFinish}
      initialValues={props.initialValues}
      validateMessages={validateMessages}
    >
      {(_, formInstance) => (
        <>
          <Form.Item name="name" label="Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>

          <Form.Item label="Base Url" name="base_url" >
            <Row gutter={8}>
              <Col span={21}>
                <Form.Item
                  label="Base Url"
                  name="base_url"
                  noStyle
                  rules={[{ required: true, type: 'url' }]}
                >
                  <Input />
                </Form.Item>
              </Col>
              <Col span={3}>
                <Button
                  href={formInstance.getFieldValue("base_url")}
                  disabled={formInstance.getFieldError("base_url").length !== 0}
                  type="text"
                  target="_blank"
                  rel="noreferrer noopener"
                >
                  <LinkOutlined />
                </Button>
              </Col>
            </Row>
          </Form.Item>

          <Form.Item name="scrape_method" label="Scrape Method">
            <Select options={scrapes} />
          </Form.Item>
          <Form.Item name="cron" label="Schedule">
            <Select options={schedules} />
          </Form.Item>
          <Form.Item name="tags" label="Tags">
            <Select mode="tags" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Submit
              </Button>
              <Link to="/sites">
                <Button htmlType="submit">Cancel</Button>
              </Link>
            </Space>
          </Form.Item>
        </>
      )
      }
    </Form >
  );
}
