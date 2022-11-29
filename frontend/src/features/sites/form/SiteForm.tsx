import { Card, Col, Form, Input, Row, Select, Typography } from 'antd';
import { FormInstance } from 'antd/lib/form/Form';
import { Site, CollectionMethod } from '../types';
import { UrlFormFields } from './UrlFormField';
import { CollectionSettings } from './CollectionSettings';
import { SiteStatus } from '../siteStatus';
import { Assignee } from './AssigneeInput';
import { SiteStatusRadio as Status } from './SiteStatusRadio';
import { CommentWall } from '../../comments/CommentWall';
import { useParams } from 'react-router-dom';
import { useGetSiteQuery, useLazyGetSiteByNameQuery } from '../sitesApi';
import { Rule } from 'antd/lib/form';
import { useCallback } from 'react';

const useMustBeUniqueNameRule = () => {
  const { siteId } = useParams();
  const { data: currentSite } = useGetSiteQuery(siteId);
  const [getSiteByName] = useLazyGetSiteByNameQuery();

  const mustBeUniqueName = useCallback(
    () => ({
      async validator(_rule: Rule, newName: string) {
        if (currentSite && newName === currentSite.name) {
          return Promise.resolve();
        }
        const { data: site } = await getSiteByName(newName);
        if (site) {
          return Promise.reject(`Site name "${site.name}" already exists`);
        }
        return Promise.resolve();
      },
    }),
    [currentSite, getSiteByName]
  );
  return mustBeUniqueName;
};

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
    wait_for_timeout_ms: '500',
    follow_links: false,
    follow_link_keywords: [],
    follow_link_url_keywords: [],
    searchable: false,
    searchable_playbook: null,
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
  const mustBeUniqueName = useMustBeUniqueNameRule();
  return (
    <>
      <Typography.Title level={3}>Site Information</Typography.Title>
      <Form.Item name="name" label="Name" rules={[{ required: true }, mustBeUniqueName]}>
        <Input />
      </Form.Item>
      <UrlFormFields initialValues={initialValues} />
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
      validateTrigger={['onBlur']}
    >
      <Row gutter={16} className="flex pb-[20%]">
        <Col span={12} className="space-y-4">
          <Card>
            <SiteInformation {...props} />
          </Card>
          {initialValues._id ? (
            <Card>
              <Typography.Title level={3}>Notes</Typography.Title>
              <CommentWall targetId={initialValues._id} />
            </Card>
          ) : null}
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
