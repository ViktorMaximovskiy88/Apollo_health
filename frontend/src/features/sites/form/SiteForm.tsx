import { Card, Col, Form, Input, Row, Select, Typography } from 'antd';
import { FormInstance } from 'antd/lib/form/Form';
import { Site, CollectionMethod } from '../types';
import { UrlFormFields } from './UrlFormField';
import { CollectionSettings } from './CollectionSettings';
import { SiteStatus } from '../siteStatus';
import { Assignee } from './AssigneeInput';
import { SiteStatusRadio as Status } from './SiteStatusRadio';

const buildInitialValues = () => ({
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
    focus_section_configs: [],
    allow_docdoc_updates: false,
  },
  doc_type_threshold_override: false,
  doc_type_threshold: 0.75,
  lineage_threshold_override: false,
  lineage_threshold: 0.75,
});

/* eslint-disable no-template-curly-in-string */
const validateMessages = {
  required: '${label} is required!',
  types: {
    url: '${label} is not a valid url!',
  },
};
/* eslint-enable no-template-curly-in-string */

const SiteInformation = ({ initialValues }: { initialValues?: Site }) => {
  const form = Form.useFormInstance();
  return (
    <>
      <Typography.Title level={3}>Site Information</Typography.Title>
      <Form.Item name="name" label="Name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <UrlFormFields initialValues={initialValues} form={form} />
      <Form.Item name="tags" label="Site Tags">
        <Select mode="tags" />
      </Form.Item>
      <Status />
      <Assignee />
    </>
  );
};

export function SiteForm(props: {
  onFinish: (update: Partial<Site>) => void;
  initialValues?: Site;
  form: FormInstance;
}) {
  let initialValues: Partial<Site> | undefined = props.initialValues;
  if (!initialValues) {
    initialValues = buildInitialValues();
  }

  return (
    <Form
      layout="vertical"
      form={props.form}
      requiredMark={false}
      onFinish={props.onFinish}
      initialValues={initialValues}
      validateMessages={validateMessages}
    >
      <Row gutter={16} className="flex pb-[20%]">
        <Col span={12}>
          <Card>
            <SiteInformation {...props} />
          </Card>
        </Col>
        <Col span={12}>
          <Card>
            <CollectionSettings initialValues={initialValues} />
          </Card>
        </Col>
      </Row>
    </Form>
  );
}
