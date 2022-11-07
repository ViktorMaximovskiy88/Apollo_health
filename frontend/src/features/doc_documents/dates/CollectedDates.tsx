import { Form } from 'antd';
import { ListDatePicker } from '../../../components';
import { useGetDocDocumentQuery } from '../docDocumentApi';

export function FirstCollectedDate({ onFieldChange }: { onFieldChange: () => void }) {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;
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
}

export function LastCollectedDate({ onFieldChange }: { onFieldChange: () => void }) {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;
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
}
