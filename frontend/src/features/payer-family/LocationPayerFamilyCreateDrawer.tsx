import { Button, Drawer, Form, Input } from 'antd';
import { useLazyGetPayerFamilyByNameQuery } from './payerFamilyApi';
import { DocDocumentLocation } from '../doc_documents/locations/types';
import { useAddPayerFamilyMutation } from './payerFamilyApi';
import { useForm } from 'antd/lib/form/Form';
import { Rule } from 'antd/lib/form';
import { useCallback, useState } from 'react';
import { PayerFamily } from './types';
import { PayerFamilyInfoForm } from './PayerFamilyInfoForm';
import { CloseOutlined, WarningFilled } from '@ant-design/icons';

interface PayerFamilyCreateDrawerPropTypes {
  location?: DocDocumentLocation;
  open?: boolean;
  onClose: () => void;
  onSave: (newPayerFamily: PayerFamily) => void;
  mask?: boolean;
}

export const PayerFamilyCreateDrawer = (props: PayerFamilyCreateDrawerPropTypes) => {
  const { location, onSave, open, mask } = props;
  const [form] = useForm();
  const [getPayerFamilyByName] = useLazyGetPayerFamilyByNameQuery();

  const [addPayerFamily, { isLoading }] = useAddPayerFamilyMutation();
  const [payerInfoError, setPayerInfoError] = useState<boolean>(false);

  const handleClose = useCallback(() => {
    props.onClose();
    setPayerInfoError(false);
    form.resetFields();
  }, [form, props]);

  const onFinish = useCallback(
    async (values: Partial<PayerFamily>) => {
      const payerFamily = await addPayerFamily(values).unwrap();
      onSave(payerFamily);
      form.resetFields();
    },
    [addPayerFamily, onSave, form]
  );

  const onSubmit = useCallback(async () => {
    const { payer_ids, channels, benefits, plan_types, regions } = form.getFieldsValue(true);
    if (
      !payer_ids.length &&
      !channels.length &&
      !benefits.length &&
      !plan_types.length &&
      !regions.length
    ) {
      setPayerInfoError(true);
      return;
    }
    form.submit();
  }, [form]);

  return (
    <Drawer
      open={open}
      title={<>Add Payer Family {location?.site_name ? `for ${location.site_name}` : null}</>}
      width="30%"
      placement="left"
      closable={false}
      mask={mask}
      extra={
        <Button type="text" onClick={handleClose}>
          <CloseOutlined />
        </Button>
      }
      onClose={handleClose}
    >
      <Form
        form={form}
        layout="vertical"
        disabled={isLoading}
        autoComplete="off"
        requiredMark={false}
        validateTrigger={['onBlur']}
        onFinish={onFinish}
        initialValues={{
          payer_ids: [],
          channels: [],
          benefits: [],
          plan_types: [],
          regions: [],
        }}
      >
        {location?.site_name ? (
          <div className="flex">
            <div className="flex-1 mt-2 mb-4">
              <h3>Site</h3>
              <div>{location.site_name}</div>
            </div>
          </div>
        ) : null}
        <Input.Group className="space-x-2 flex">
          <Form.Item
            label="Name"
            name="name"
            className="w-96 mr-5"
            rules={[
              { required: true, message: 'Please input a payer family name' },
              mustBeUniqueName(getPayerFamilyByName),
            ]}
          >
            <Input />
          </Form.Item>
        </Input.Group>

        <PayerFamilyInfoForm />

        <div className="space-x-2 flex justify-end">
          {payerInfoError ? (
            <>
              <WarningFilled className="text-red-600" />
              <span className="text-red-600">'At least one payer value is required'</span>
            </>
          ) : null}

          <Button onClick={handleClose}>Cancel</Button>
          <Button type="primary" onClick={onSubmit} loading={isLoading}>
            Submit
          </Button>
        </div>
      </Form>
    </Drawer>
  );
};

// asyncValidator because rtk query makes this tough without hooks/dispatch
export function mustBeUniqueName(asyncValidator: Function) {
  return {
    async validator(_rule: Rule, value: string) {
      const { data: payerFamily } = await asyncValidator({ name: value });
      if (payerFamily) {
        return Promise.reject(`Payer family name "${payerFamily.name}" already exists`);
      }
      return Promise.resolve();
    },
  };
}
