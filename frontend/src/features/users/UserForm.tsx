import { Form, Input, Switch, Select, Space, Button } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { Link } from 'react-router-dom';
import { User } from './types';

export function UserForm(props: {
  onFinish: (user: Partial<User>) => void;
  initialValues?: User;
}) {
  const [form] = useForm();

  const roles = [
    { value: 'Scrape Admin' },
    { value: 'Dashboard' },
    { value: 'Assessor' },
    { value: 'Admin' },
  ];

  return (
    <Form
      layout="vertical"
      form={form}
      wrapperCol={{ span: 7 }}
      requiredMark={false}
      onFinish={props.onFinish}
      initialValues={props.initialValues}
    >
      <Form.Item name="full_name" label="Name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item
        name="email"
        label="Email"
        rules={[{ required: true, type: 'email' }]}
      >
        <Input />
      </Form.Item>
      <Form.Item name="password" label="Password">
        <Input type="password"/>
      </Form.Item>
      <Form.Item name="is_admin" label="Is Admin" valuePropName="checked">
        <Switch />
      </Form.Item>
      <Form.Item name="roles" label="Roles">
        <Select mode="multiple" options={roles} />
      </Form.Item>
      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit">
            Submit
          </Button>
          <Link to="/users">
            <Button htmlType="submit">Cancel</Button>
          </Link>
        </Space>
      </Form.Item>
    </Form>
  );
}
