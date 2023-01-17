import { WarningOutlined } from '@ant-design/icons';
import { Collapse, Form } from 'antd';
import { FormInstance } from 'rc-field-form';
import { useState } from 'react';
import { DocDate } from './DocDate';

export enum DateName {
  EffectiveDate = 'effective_date',
  EndDate = 'end_date',
  LastUpdatedDate = 'last_updated_date',
  LastReviewedDate = 'last_reviewed_date',
  NextReviewDate = 'next_review_date',
  NextUpdateDate = 'next_update_date',
  PublishedDate = 'published_date',
  FirstCollectedDate = 'first_collected_date',
  LastCollectedDate = 'last_collected_date',
}

const buildHasDateError = (form: FormInstance) =>
  form
    .getFieldsError([...Object.values(DateName)])
    .reduce((hasError, current) => hasError || !!current.errors.length, false);

const Header = () => {
  const form = Form.useFormInstance();
  const hasDateError = buildHasDateError(form);
  return <>Dates {hasDateError ? <WarningOutlined className="text-red-500" /> : null}</>;
};

export function DateFields(props: { onFieldChange: () => void }) {
  const [collapseOpen, setCollapseOpen] = useState<boolean>(false);
  return (
    <>
      <Collapse
        activeKey={collapseOpen ? '1' : ''}
        onChange={(newActiveKeys) => setCollapseOpen(!!newActiveKeys.length)}
        className="bg-white"
      >
        <Collapse.Panel header={<Header />} key="1" forceRender>
          <div className="flex flex-1 space-x-8">
            <DocDate
              name={DateName.EffectiveDate}
              label="Effective Date"
              setCollapseOpen={() => setCollapseOpen(true)}
              {...props}
            />
            <DocDate
              setCollapseOpen={() => setCollapseOpen(true)}
              name={DateName.EndDate}
              label="End Date"
              beforeDateName={DateName.EffectiveDate}
              beforeDateLabel="Effective Date"
              {...props}
            />
            <DocDate
              setCollapseOpen={() => setCollapseOpen(true)}
              name={DateName.LastUpdatedDate}
              label="Last Updated Date"
              {...props}
            />
          </div>

          <div className="flex flex-1 space-x-8">
            <DocDate
              setCollapseOpen={() => setCollapseOpen(true)}
              name={DateName.LastReviewedDate}
              label="Last Reviewed Date"
              {...props}
            />
            <DocDate
              setCollapseOpen={() => setCollapseOpen(true)}
              name={DateName.NextReviewDate}
              label="Next Review Date"
              beforeDateName={DateName.LastReviewedDate}
              beforeDateLabel="Last Reviewed Date"
              {...props}
            />
            <DocDate
              setCollapseOpen={() => setCollapseOpen(true)}
              name={DateName.NextUpdateDate}
              label="Next Update Date"
              beforeDateName={DateName.LastUpdatedDate}
              beforeDateLabel="Last Updated Date"
              {...props}
            />
          </div>

          <div className="flex flex-1 space-x-8">
            <DocDate
              setCollapseOpen={() => setCollapseOpen(true)}
              name={DateName.PublishedDate}
              label="Published Date"
              {...props}
            />
            <DocDate
              setCollapseOpen={() => setCollapseOpen(true)}
              name={DateName.FirstCollectedDate}
              label="First Collected Date"
              disabled
              {...props}
            />
            <DocDate
              setCollapseOpen={() => setCollapseOpen(true)}
              name={DateName.LastCollectedDate}
              label="Last Collected Date"
              disabled
              {...props}
            />
          </div>
        </Collapse.Panel>
      </Collapse>
    </>
  );
}
