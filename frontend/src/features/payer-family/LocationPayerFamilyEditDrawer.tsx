import { Button, Drawer, Form, Input } from 'antd';
import { DocDocumentLocation } from '../doc_documents/locations/types';
import {
  useUpdatePayerFamilyMutation,
  useLazyGetPayerFamilyByNameQuery,
  useGetPayerFamilyQuery,
  useLazyConvertPayerFamilyDataQuery,
} from './payerFamilyApi';
import { Rule } from 'antd/lib/form';
import { useForm } from 'antd/lib/form/Form';
import { useCallback, useEffect, useState } from 'react';
import { PayerFamilyInfoForm } from './PayerFamilyInfoForm';
import { PayerFamily } from './types';
import { CloseOutlined, WarningFilled } from '@ant-design/icons';

interface PayerFamilyEditDrawerPropTypes {
  location?: DocDocumentLocation | undefined;
  payer_family_id: string;
  open?: boolean;
  onClose: () => void;
  onSave: (updatedPayerFamily: PayerFamily) => void;
  editPayerFromTable?: boolean;
  mask?: boolean;
}

export const PayerFamilyEditDrawer = (props: PayerFamilyEditDrawerPropTypes) => {
  const { location, onClose, onSave, open, payer_family_id, editPayerFromTable, mask } = props;
  const [form] = useForm();
  const { data: payerFamily } = useGetPayerFamilyQuery(payer_family_id, { skip: !payer_family_id });
  const [getPayerFamilyByName] = useLazyGetPayerFamilyByNameQuery();
  const [payerInfoError, setPayerInfoError] = useState<string>();
  const [updatePayerFamily, { isLoading }] = useUpdatePayerFamilyMutation();
  const [convertPayerFamily] = useLazyConvertPayerFamilyDataQuery();

  const onSubmit = useCallback(async () => {
    form.validateFields();
    let { name, payer_type, payer_ids, channels, benefits, plan_types, regions } =
      form.getFieldsValue(true);
    if (
      !payer_ids?.length &&
      !channels?.length &&
      !benefits?.length &&
      !plan_types?.length &&
      !regions?.length
    ) {
      setPayerInfoError('At least one payer value is required');
      return;
    }
    try {
      await convertPayerFamily({
        payerType: 'plan',
        body: { name, payer_type, payer_ids, channels, benefits, plan_types, regions },
      }).unwrap();
    } catch (err: any) {
      setPayerInfoError(err.data.detail);
      return;
    }

    form.submit();
  }, [form]);

  useEffect(() => {
    form.setFieldsValue(payerFamily);
  }, [payerFamily]);

  const onFinish = useCallback(
    async (values: Partial<PayerFamily>) => {
      const payerFamily = await updatePayerFamily({ ...values, _id: payer_family_id }).unwrap();

      onSave(payerFamily);
      form.resetFields();
    },
    [updatePayerFamily, payer_family_id, onSave, form]
  );

  if (editPayerFromTable) {
    if (!payerFamily) {
      return <></>;
    }
  } else if (!payerFamily || !location) {
    return <></>;
  }

  return (
    <Drawer
      open={open}
      title={<>Edit Payer Family {location?.site_name ? `for ${location.site_name}` : ''}</>}
      width="30%"
      forceRender
      placement="left"
      closable={false}
      mask={mask}
      extra={
        <Button type="text" onClick={onClose}>
          <CloseOutlined />
        </Button>
      }
    >
      <Form
        form={form}
        initialValues={payerFamily}
        layout="vertical"
        disabled={isLoading}
        autoComplete="off"
        requiredMark={false}
        validateTrigger={['onBlur']}
        onFinish={onFinish}
      >
        {location?.site_name ? (
          <>
            <h3>Site</h3>
            <div className="flex">
              <div className="flex-1 mt-2 mb-4">
                <div>{location?.site_name}</div>
              </div>
            </div>
          </>
        ) : null}

        <Form.Item
          label="Name"
          name="name"
          className="w-96 mr-5"
          rules={[
            { required: true, message: 'Please input a payer family name' },
            mustBeUniqueName(getPayerFamilyByName, payerFamily?.name),
          ]}
        >
          <Input />
        </Form.Item>

        <PayerFamilyInfoForm />
        <div className="space-x-2 flex justify-end">
          {payerInfoError ? (
            <>
              <WarningFilled className="text-red-600" />
              <span className="text-red-600">{payerInfoError}</span>
            </>
          ) : null}
          <Button onClick={onClose}>Cancel</Button>
          <Button type="primary" onClick={onSubmit} loading={isLoading}>
            Submit
          </Button>
        </div>
      </Form>
    </Drawer>
  );
};

// asyncValidator because rtk query makes this tough without hooks/dispatch
export function mustBeUniqueName(asyncValidator: Function, name: string = '') {
  return {
    async validator(_rule: Rule, value: string) {
      if (value === name) {
        return Promise.resolve();
      }
      const { data: payerFamily } = await asyncValidator({ name: value });
      if (payerFamily) {
        return Promise.reject(`Payer family name "${payerFamily.name}" already exists`);
      }
      return Promise.resolve();
    },
  };
}
