import { Collapse } from 'antd';
import { FirstCollectedDate, LastCollectedDate } from './dates/CollectedDates';
import { EffectiveDate, EndDate } from './dates/EffectiveAndEndDates';
import { PublishedDate } from './dates/PublishedDate';
import { LastReviewedDate, NextReviewDate } from './dates/ReviewDates';
import { LastUpdatedDate, NextUpdateDate } from './dates/UpdateDates';

export function DateFields(props: { onFieldChange: () => void }) {
  return (
    <Collapse className="bg-white">
      <Collapse.Panel header="Dates" key="1" forceRender>
        <div className="flex flex-1 space-x-8">
          <EffectiveDate {...props} />
          <EndDate {...props} />
          <LastUpdatedDate {...props} />
        </div>

        <div className="flex flex-1 space-x-8">
          <LastReviewedDate {...props} />
          <NextReviewDate {...props} />
          <NextUpdateDate {...props} />
        </div>

        <div className="flex flex-1 space-x-8">
          <PublishedDate {...props} />
          <FirstCollectedDate {...props} />
          <LastCollectedDate {...props} />
        </div>
      </Collapse.Panel>
    </Collapse>
  );
}
