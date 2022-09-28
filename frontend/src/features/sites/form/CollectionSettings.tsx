import { Input, Form, Select, Radio, Switch, Typography } from 'antd';

import { CollectionMethod, ScrapeMethod, Site } from '../types';
import {
  DocumentExtensions,
  UrlKeywords,
  ProxyExclusions,
  WaitFor,
  WaitForTimeout,
  SearchInFrames,
  AllowDocDocUpdate,
} from './ScrapeConfigFields';

import { AttrSelectors } from './AttrSelectorField';
import { FocusTherapyConfig } from './FocusTherapyConfig';
import { HtmlScrapeConfig } from './HtmlScrapeConfig';
import { SearchTokens } from './SearchTokens';

function CollectionMethodRadio() {
  const collections = [
    { value: CollectionMethod.Automated, label: 'Automated' },
    { value: CollectionMethod.Manual, label: 'Manual' },
  ];

  return (
    <Form.Item name="collection_method" label="Collection Method">
      <Radio.Group options={collections} optionType="button" buttonStyle="solid" />
    </Form.Item>
  );
}

function ScrapeMethodSelect() {
  const scrapes = [
    { value: ScrapeMethod.Simple, label: 'Simple Document Scrape' },
    { value: ScrapeMethod.Html, label: 'HTML Scrape' },
  ];

  return (
    <Form.Item name="scrape_method" label="Scrape Method">
      <Select options={scrapes} />
    </Form.Item>
  );
}

function Schedule() {
  const schedules = [
    { value: '0 16 * * *', label: 'Daily' },
    { value: '0 16 * * 0', label: 'Weekly' },
    { value: '0 16 1 * *', label: 'Monthly' },
  ];

  return (
    <Form.Item name="cron" label="Schedule">
      <Radio.Group options={schedules} optionType="button" buttonStyle="solid" />
    </Form.Item>
  );
}

function FollowLinks() {
  const form = Form.useFormInstance();
  const followLinks = Form.useWatch(['scrape_method_configuration', 'follow_links']);
  function validateFollowLinks(fieldInfo: any, value: string) {
    if (value.length === 0) {
      const namePaths = [
        ['scrape_method_configuration', 'follow_link_keywords'],
        ['scrape_method_configuration', 'follow_link_url_keywords'],
      ];
      const currentNamePath = fieldInfo.field.split('.');
      const otherNamePath = namePaths
        .filter((path) => {
          return !path.every((ele) => currentNamePath.includes(ele));
        })
        .flat();
      const otherValue = form.getFieldValue(otherNamePath);

      if (otherValue.length === 0) {
        return Promise.reject(
          new Error('You must provide a Link or URL Keyword with Follow Links enabled')
        );
      }
    }

    return Promise.resolve();
  }

  return (
    <div className="flex space-x-5">
      <Form.Item
        name={['scrape_method_configuration', 'follow_links']}
        label="Follow Links"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>
      {followLinks && (
        <div className="flex grow space-x-5">
          <Form.Item
            className="grow"
            name={['scrape_method_configuration', 'follow_link_keywords']}
            label="Follow Link Keywords"
            rules={[
              {
                validator: (field, value) => validateFollowLinks(field, value),
              },
            ]}
          >
            <Select mode="tags" />
          </Form.Item>
          <Form.Item
            className="grow"
            name={['scrape_method_configuration', 'follow_link_url_keywords']}
            label="Follow Link URL Keywords"
            rules={[
              {
                validator: (field, value) => validateFollowLinks(field, value),
              },
            ]}
          >
            <Select mode="tags" />
          </Form.Item>
        </div>
      )}
    </div>
  );
}

interface CollectionSettingsPropTypes {
  initialValues: Partial<Site>;
}
export function CollectionSettings({ initialValues }: CollectionSettingsPropTypes) {
  const currentScrapeMethod: ScrapeMethod = Form.useWatch('scrape_method');
  return (
    <>
      <Typography.Title level={3}>Collection Settings</Typography.Title>
      <CollectionMethodRadio />
      <Form.Item
        noStyle
        shouldUpdate={(prevValues, currentValues) =>
          prevValues.collection_method !== currentValues.collection_method
        }
      >
        {({ getFieldValue }) =>
          getFieldValue('collection_method') === CollectionMethod.Automated ? (
            <>
              <SearchTokens />
              <Form.Item name="playbook" label="Playbook">
                <Input.TextArea />
              </Form.Item>
              <ScrapeMethodSelect />
              {currentScrapeMethod === ScrapeMethod.Html && <HtmlScrapeConfig />}
              <DocumentExtensions />
              <UrlKeywords />
              <ProxyExclusions />
              <WaitFor />
              <WaitForTimeout />
              <Schedule />
              <FollowLinks />
              <SearchInFrames />
              <AllowDocDocUpdate />
              <FocusTherapyConfig initialValues={initialValues} />
              <AttrSelectors
                displayIsResource
                parentName={['scrape_method_configuration', 'attr_selectors']}
                title={<label className="font-semibold">Custom Selectors</label>}
              />
            </>
          ) : null
        }
      </Form.Item>
    </>
  );
}
