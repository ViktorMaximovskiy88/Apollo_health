import { Form } from 'antd';
import { ListDatePicker } from '../../components';
import { useGetDocDocumentQuery } from './docDocumentApi';

export type DateName =
  | 'end_date'
  | 'effective_date'
  | 'published_date'
  | 'last_reviewed_date'
  | 'next_review_date'
  | 'last_updated_date'
  | 'next_update_date'
  | 'last_collected_date'
  | 'first_collected_date';

export type DateLabel =
  | 'End Date'
  | 'Effective Date'
  | 'Published Date'
  | 'Last Reviewed Date'
  | 'Next Review Date'
  | 'Last Updated Date'
  | 'Next Update Date'
  | 'Last Collected Date'
  | 'First Collected Date';

export function DocDate(props: {
  name: DateName;
  label: DateLabel;
  beforeDateName?: DateName;
  beforeDateLabel?: DateLabel;
  onFieldChange: () => void;
  disabled?: boolean;
}) {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;
  return (
    <Form.Item
      name={props.name}
      className="flex-1"
      label={props.label}
      rules={[
        {
          validator: (_rule, value) => {
            if (!props.beforeDateName) return Promise.resolve();
            const afterDate = form.getFieldValue(props.beforeDateName);
            if (!value || !afterDate || afterDate < value) return Promise.resolve();
            return Promise.reject(`${props.label} must come after ${props.beforeDateLabel}`);
          },
        },
      ]}
    >
      <ListDatePicker disabled={props.disabled} dateList={doc.identified_dates} />
    </Form.Item>
  );
}
