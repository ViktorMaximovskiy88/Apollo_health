import { Collapse } from 'antd';
import { useState } from 'react';
import { DocDate } from './DocDate';

export function DateFields(props: { onFieldChange: () => void }) {
  const [collapseOpen, setCollapseOpen] = useState<boolean>(false);
  return (
    <Collapse
      activeKey={collapseOpen ? '1' : ''}
      onChange={(newActiveKeys) => setCollapseOpen(!!newActiveKeys.length)}
      className="bg-white"
    >
      <Collapse.Panel header="Dates" key="1" forceRender>
        <div className="flex flex-1 space-x-8">
          <DocDate
            name="effective_date"
            label="Effective Date"
            setCollapseOpen={() => setCollapseOpen(true)}
            {...props}
          />
          <DocDate
            setCollapseOpen={() => setCollapseOpen(true)}
            name="end_date"
            label="End Date"
            beforeDateName="effective_date"
            beforeDateLabel="Effective Date"
            {...props}
          />
          <DocDate
            setCollapseOpen={() => setCollapseOpen(true)}
            name="last_updated_date"
            label="Last Updated Date"
            {...props}
          />
        </div>

        <div className="flex flex-1 space-x-8">
          <DocDate
            setCollapseOpen={() => setCollapseOpen(true)}
            name="last_reviewed_date"
            label="Last Reviewed Date"
            {...props}
          />
          <DocDate
            setCollapseOpen={() => setCollapseOpen(true)}
            name="next_review_date"
            label="Next Review Date"
            beforeDateName="last_reviewed_date"
            beforeDateLabel="Last Reviewed Date"
            {...props}
          />
          <DocDate
            setCollapseOpen={() => setCollapseOpen(true)}
            name="next_update_date"
            label="Next Update Date"
            beforeDateName="last_updated_date"
            beforeDateLabel="Last Updated Date"
            {...props}
          />
        </div>

        <div className="flex flex-1 space-x-8">
          <DocDate
            setCollapseOpen={() => setCollapseOpen(true)}
            name="published_date"
            label="Published Date"
            {...props}
          />
          <DocDate
            setCollapseOpen={() => setCollapseOpen(true)}
            name="first_collected_date"
            label="First Collected Date"
            disabled
            {...props}
          />
          <DocDate
            setCollapseOpen={() => setCollapseOpen(true)}
            name="last_collected_date"
            label="Last Collected Date"
            disabled
            {...props}
          />
        </div>
      </Collapse.Panel>
    </Collapse>
  );
}
