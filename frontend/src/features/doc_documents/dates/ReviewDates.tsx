import { Form } from 'antd';
import { Rule } from 'antd/lib/form';
import { ListDatePicker } from '../../../components';
import { useGetDocDocumentQuery } from '../docDocumentApi';

export function LastReviewedDate({ onFieldChange }: { onFieldChange: () => void }) {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const nextReviewDate = Form.useWatch('next_review_date');
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="last_reviewed_date"
      defaultValue={doc.last_reviewed_date}
      label={'Last Reviewed Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
      rules={[
        {
          validator: (_rule: Rule, lastReviewedDate: moment.Moment): Promise<void> => {
            if (!lastReviewedDate || !nextReviewDate) return Promise.resolve();
            if (lastReviewedDate < nextReviewDate) return Promise.resolve();
            return Promise.reject('Last Review Date must come before Next Review Date.');
          },
        },
      ]}
    />
  );
}
export function NextReviewDate({ onFieldChange }: { onFieldChange: () => void }) {
  const form = Form.useFormInstance();
  const docId = form.getFieldValue('docId');
  const lastReviewedDate = Form.useWatch('last_reviewed_date');
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;
  return (
    <ListDatePicker
      form={form}
      className="flex-1"
      name="next_review_date"
      defaultValue={doc.next_review_date}
      label={'Next Review Date'}
      dateList={doc.identified_dates}
      onChange={onFieldChange}
      rules={[
        {
          validator: (_rule: Rule, nextReviewDate: moment.Moment): Promise<void> => {
            if (!lastReviewedDate || !nextReviewDate) return Promise.resolve();
            if (lastReviewedDate < nextReviewDate) return Promise.resolve();
            return Promise.reject('Last Review Date must come before Next Review Date.');
          },
        },
      ]}
    />
  );
}
