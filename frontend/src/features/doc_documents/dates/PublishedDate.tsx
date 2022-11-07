import { Form } from 'antd';
import { ListDatePicker } from '../../../components';
import { useGetDocDocumentQuery } from '../docDocumentApi';

export function PublishedDate({ onFieldChange }: { onFieldChange: () => void }) {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;
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
}
