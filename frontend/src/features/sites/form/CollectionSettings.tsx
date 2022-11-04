import { Input, Form, Select, Radio, Typography } from 'antd';

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
import { FocusTagConfig } from './FocusTagConfig';
import { HtmlScrapeConfig } from './HtmlScrapeConfig';
import { SearchTokens } from './SearchTokens';
import { FollowLinks } from './FollowLinks';
import { ThresholdWithOverride } from './ThresholdWithOverride';

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
    { value: ScrapeMethod.Html, label: 'Direct HTML Scrape' },
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
const DocumentTypeThreshold = () => (
  <ThresholdWithOverride
    overrideName="doc_type_threshold_override"
    overrideLabel="Document Type Threshold Override"
    thresholdName="doc_type_threshold"
    thresholdLabel="Document Type Threshold"
  />
);

const LineageThreshold = () => (
  <ThresholdWithOverride
    overrideName="lineage_threshold_override"
    overrideLabel="Lineage Threshold Override"
    thresholdName="lineage_threshold"
    thresholdLabel="Lineage Threshold"
  />
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
              <DocumentExtensions />
              <UrlKeywords />
              <HtmlScrapeConfig scrapeMethod={currentScrapeMethod} />
              <CustomSelectors />
              <WaitFor />
              <WaitForTimeout />
              <Schedule />
              <FollowLinks />
              <SearchTokens />
              <Playbook />
              <SearchInFrames />
              <AllowDocDocUpdate />
              <ProxyExclusions />
              <FocusTagConfig initialValues={initialValues} />
              <DocumentTypeThreshold />
              <LineageThreshold />
            </>
          ) : null
        }
      </Form.Item>
    </>
  );
}
