import { Input, Form, Select, Radio, Typography, Slider } from 'antd';

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
import { FollowLinks } from './FollowLinks';

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

const Playbook = () => (
  <Form.Item name="playbook" label="Playbook">
    <Input.TextArea />
  </Form.Item>
);
const CustomSelectors = () => (
  <AttrSelectors
    displayIsResource
    parentName={['scrape_method_configuration', 'attr_selectors']}
    title={<label className="font-semibold">Custom Selectors</label>}
  />
);

const formatter = (value?: number) => {
  if (!value) return;
  const displayedValue = Math.round(value * 100); // fix floating point math bugs
  return `${displayedValue}%`;
};

const DocumentTypeThreshold = () => (
  <Form.Item name="doc_type_threshold" label="Document Type Threshold">
    <Slider min={0} max={1} step={0.01} tipFormatter={formatter} />
  </Form.Item>
);

const LineageThreshold = () => (
  <Form.Item name="lineage_threshold" label="Lineage Threshold">
    <Slider min={0} max={1} step={0.01} tipFormatter={formatter} />
  </Form.Item>
);

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
              <ScrapeMethodSelect />
              {currentScrapeMethod === ScrapeMethod.Html ? <HtmlScrapeConfig /> : null}
              <DocumentExtensions />
              <UrlKeywords />
              <CustomSelectors />
              <ProxyExclusions />
              <WaitFor />
              <WaitForTimeout />
              <Schedule />
              <FollowLinks />
              <SearchTokens />
              <Playbook />
              <SearchInFrames />
              <AllowDocDocUpdate />
              <FocusTherapyConfig initialValues={initialValues} />
              <DocumentTypeThreshold />
              <LineageThreshold />
            </>
          ) : null
        }
      </Form.Item>
    </>
  );
}
