import { Form } from 'antd';
import { ListDatePicker } from '../../components';
import { DocDocument } from './types';

interface DateFieldPropTypes {
  doc: DocDocument;
  onFieldChange: Function;
}

const EffectiveDate = ({ doc, onFieldChange }: DateFieldPropTypes) => {
  const form = Form.useFormInstance();
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="effective_date"
      defaultValue={doc.effective_date}
      label={'Effective Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
    />
  );
};
const EndDate = ({ doc, onFieldChange }: DateFieldPropTypes) => {
  const form = Form.useFormInstance();
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="end_date"
      defaultValue={doc.end_date}
      label={'End Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
    />
  );
};
const LastUpdatedDate = ({ doc, onFieldChange }: DateFieldPropTypes) => {
  const form = Form.useFormInstance();
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="last_updated_date"
      defaultValue={doc.last_updated_date}
      label={'Last Updated Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
    />
  );
};
const LastReviewedDate = ({ doc, onFieldChange }: DateFieldPropTypes) => {
  const form = Form.useFormInstance();
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="last_reviewed_date"
      defaultValue={doc.last_reviewed_date}
      label={'Last Reviewed Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
    />
  );
};
const NextReviewedDate = ({ doc, onFieldChange }: DateFieldPropTypes) => {
  const form = Form.useFormInstance();
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="next_review_date"
      defaultValue={doc.next_review_date}
      label={'Next Review Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
    />
  );
};
const NextUpdateDate = ({ doc, onFieldChange }: DateFieldPropTypes) => {
  const form = Form.useFormInstance();
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="next_update_date"
      defaultValue={doc.next_update_date}
      label={'Next Update Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
    />
  );
};
const PublishedDate = ({ doc, onFieldChange }: DateFieldPropTypes) => {
  const form = Form.useFormInstance();
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="published_date"
      defaultValue={doc.published_date}
      label={'Published Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
    />
  );
};
const FirstCollectedDate = ({ doc, onFieldChange }: DateFieldPropTypes) => {
  const form = Form.useFormInstance();
  return (
    <ListDatePicker
      disabled
      form={form}
      className="flex-1"
      name="first_collected_date"
      defaultValue={doc.first_collected_date}
      label={'First Collected Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
    />
  );
};
const LastCollectedDate = ({ doc, onFieldChange }: DateFieldPropTypes) => {
  const form = Form.useFormInstance();
  return (
    <ListDatePicker
      disabled
      form={form}
      className="flex-1"
      name="last_collected_date"
      defaultValue={doc.last_collected_date}
      label={'Last Collected Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
    />
  );
};

export function DateFields(props: DateFieldPropTypes) {
  return (
    <>
      <div className="flex flex-1 space-x-8">
        <EffectiveDate {...props} />
        <EndDate {...props} />
        <LastUpdatedDate {...props} />
      </div>

      <div className="flex flex-1 space-x-8">
        <LastReviewedDate {...props} />
        <NextReviewedDate {...props} />
        <NextUpdateDate {...props} />
      </div>

      <div className="flex flex-1 space-x-8">
        <PublishedDate {...props} />
        <FirstCollectedDate {...props} />
        <LastCollectedDate {...props} />
      </div>
    </>
  );
}
