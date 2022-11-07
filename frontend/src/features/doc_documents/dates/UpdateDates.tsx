import { Form } from 'antd';
import { Rule } from 'antd/lib/form';
import { ListDatePicker } from '../../../components';
import { useGetDocDocumentQuery } from '../docDocumentApi';

export function LastUpdatedDate({ onFieldChange }: { onFieldChange: () => void }) {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const nextUpdateDate = Form.useWatch('next_update_date');
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="last_updated_date"
      defaultValue={doc.last_updated_date}
      label={'Last Updated Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
      rules={[
        {
          validator: (_rule: Rule, lastUpdatedDate: moment.Moment): Promise<void> => {
            if (!lastUpdatedDate || !nextUpdateDate) return Promise.resolve();
            if (lastUpdatedDate < nextUpdateDate) return Promise.resolve();
            return Promise.reject('Last Updated Date must come before Next Update Date.');
          },
        },
      ]}
    />
  );
}

export function NextUpdateDate({ onFieldChange }: { onFieldChange: () => void }) {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const lastUpdatedDate = Form.useWatch('last_updated_date');
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="next_update_date"
      defaultValue={doc.next_update_date}
      label={'Next Update Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
      rules={[
        {
          validator: (_rule: Rule, nextUpdateDate: moment.Moment): Promise<void> => {
            if (!lastUpdatedDate || !nextUpdateDate) return Promise.resolve();
            if (lastUpdatedDate < nextUpdateDate) return Promise.resolve();
            return Promise.reject('Last Updated Date must come before Next Update Date.');
          },
        },
      ]}
    />
  );
}
