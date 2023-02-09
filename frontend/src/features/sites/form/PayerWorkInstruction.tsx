import { Form, Input } from 'antd';
import { LinkIcon } from '../../../components';

const Url = () => (
  <Form.Item
    className="grow mb-0"
    hasFeedback
    label="Payer Work Instructions"
    name="payer_work_instructions"
    rules={[
      {
        required: false,
        type: 'url',
      },
    ]}
    validateTrigger="onBlur"
  >
    <Input.TextArea autoSize={{ minRows: 1, maxRows: 3 }} />
  </Form.Item>
);

const LinkButton = () => {
  const form = Form.useFormInstance();
  const payerWorkInstructions = Form.useWatch('payer_work_instructions');
  return (
    <Form.Item label=" " shouldUpdate className="mb-0">
      {() => (
        <>
          {payerWorkInstructions && !form.getFieldError('payer_work_instructions').length ? (
            <LinkIcon href={payerWorkInstructions} />
          ) : null}
        </>
      )}
    </Form.Item>
  );
};

export function PayerWorkInstruction() {
  return (
    <Input.Group className="space-x-2 flex">
      <Url />
      <LinkButton />
    </Input.Group>
  );
}
