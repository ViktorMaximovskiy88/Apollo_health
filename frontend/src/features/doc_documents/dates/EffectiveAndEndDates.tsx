import { Form } from 'antd';
import { Rule } from 'antd/lib/form';
import { ListDatePicker } from '../../../components';
import { useGetDocDocumentQuery } from '../docDocumentApi';

export function EffectiveDate({ onFieldChange }: { onFieldChange: () => void }) {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const endDate = Form.useWatch('end_date');
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="effective_date"
      defaultValue={doc.effective_date}
      label={'Effective Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
      rules={[
        {
          validator: (_rule: Rule, effectiveDate: moment.Moment): Promise<void> => {
            if (!effectiveDate || !endDate) return Promise.resolve();
            if (effectiveDate < endDate) return Promise.resolve();
            return Promise.reject('Effective Date must come before End Date.');
          },
        },
      ]}
    />
  );
}
export function EndDate({ onFieldChange }: { onFieldChange: () => void }) {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const effectiveDate = Form.useWatch('effective_date');
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="end_date"
      defaultValue={doc.end_date}
      label={'End Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
      rules={[
        {
          validator: (_rule: Rule, endDate: moment.Moment): Promise<void> => {
            if (!effectiveDate || !endDate) return Promise.resolve();
            if (effectiveDate < endDate) return Promise.resolve();
            return Promise.reject('Effective Date must come before End Date.');
          },
        },
      ]}
    />
  );
}
