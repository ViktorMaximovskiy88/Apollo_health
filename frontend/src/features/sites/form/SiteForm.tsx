import { Button, Card, Col, Form, Input, Row, Select, Space, Typography } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { Link } from 'react-router-dom';
import { Site, CollectionMethod } from '../types';
import { UrlFormFields } from './UrlFormField';
import { CollectionMethodComponent } from './CollectionMethod';
import { SiteStatus } from '../siteStatus';
import { Assignee } from './AssigneeInput';
import { SiteSubmitButton as Submit } from './SiteSubmitButton';
import { ToggleReadOnly } from './ToggleReadOnly';
import { SiteStatusRadio as Status } from './SiteStatusRadio';

export function SiteForm(props: {
  onFinish: (update: Partial<Site>) => void;
  initialValues?: Site;
  readOnly?: boolean;
  setReadOnly?: (readOnly: boolean) => void;
}) {
  const [form] = useForm();

  let initialValues: Partial<Site> | undefined = props.initialValues;
  if (!initialValues) {
    initialValues = {
      scrape_method: 'SimpleDocumentScrape',
      collection_method: CollectionMethod.Automated,
      cron: '0 16 * * *',
      tags: [],
      status: SiteStatus.New,
      base_urls: [{ url: '', name: '', status: 'ACTIVE' }],
      scrape_method_configuration: {
        document_extensions: ['pdf'],
        url_keywords: [],
        proxy_exclusions: [],
        wait_for: [],
        follow_links: false,
        follow_link_keywords: [],
        follow_link_url_keywords: [],
        searchable: false,
        searchable_type: null,
        searchable_input: null,
        searchable_submit: null,
        attr_selectors: [],
        html_attr_selectors: [],
        html_exclusion_selectors: [],
        focus_therapy_configs: [],
        allow_docdoc_updates: false,
      },
    };
  }

  /* eslint-disable no-template-curly-in-string */
  const validateMessages = {
    required: '${label} is required!',
    types: {
      url: '${label} is not a valid url!',
    },
  };
  /* eslint-enable no-template-curly-in-string */

  return (
    <Form
      layout="vertical"
      form={form}
      requiredMark={false}
      onFinish={props.onFinish}
      initialValues={initialValues}
      validateMessages={validateMessages}
    >
      <Row gutter={16} className="flex pb-[20%]">
        <Col span={16}>
          <Card>
            <Typography.Title level={3}>Site Information</Typography.Title>
            <Form.Item name="name" label="Name" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <UrlFormFields initialValues={props.initialValues} form={form} />
            <Form.Item name="tags" label="Site Tags">
              <Select mode="tags" />
            </Form.Item>
            <Status />
            <Assignee />
            {props.readOnly ? (
              <ToggleReadOnly setReadOnly={props.setReadOnly} form={form} />
            ) : (
              <Form.Item>
                <Space>
                  <Submit form={form} />
                  <Link to="/sites">
                    <Button htmlType="submit">Cancel</Button>
                  </Link>
                </Space>
              </Form.Item>
            )}
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Typography.Title level={3}>Collection Settings</Typography.Title>
            <CollectionMethodComponent initialValues={initialValues} />
          </Card>
        </Col>
      </Row>
    </Form>
  );
}
