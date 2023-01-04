import { Button, Drawer, Form, Input } from 'antd';
import { DocDocumentLocation } from '../doc_documents/locations/types';
import {
  useUpdatePayerFamilyMutation,
  useLazyGetPayerFamilyByNameQuery,
  useGetPayerFamilyQuery,
  useLazyConvertPayerFamilyDataQuery,
  useLazyGetPayerFamiliesQuery,
} from './payerFamilyApi';
import { Rule } from 'antd/lib/form';
import { useForm } from 'antd/lib/form/Form';
import { ReactNode, useCallback, useEffect, useState } from 'react';
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
  const [payerInfoError, setPayerInfoError] = useState<ReactNode>();
  const [updatePayerFamily, { isLoading }] = useUpdatePayerFamilyMutation();
  const [convertPayerFamily] = useLazyConvertPayerFamilyDataQuery();
  const [queryPf] = useLazyGetPayerFamiliesQuery();

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
      const { data: existingPfs } = await queryPf({
        limit: 1,
        filterValue: [
          { name: '_id', value: payer_family_id, type: 'string', operator: 'neq' },
          { name: 'payer_type', value: payer_type, type: 'string', operator: 'eq' },
          { name: 'payer_ids', value: payer_ids, type: 'string', operator: 'leq' },
          { name: 'plan_types', value: plan_types, type: 'string', operator: 'leq' },
          { name: 'regions', value: regions, type: 'string', operator: 'leq' },
          { name: 'channels', value: channels, type: 'string', operator: 'leq' },
          { name: 'benefits', value: channels, type: 'string', operator: 'leq' },
        ],
      }).unwrap();
      const existingPf = existingPfs[0];
      if (existingPf) {
        const message = `Payer Family '${existingPf.name}' already matches this criteria.`;
        setPayerInfoError(message);
        return;
      }
    } catch (err: any) {}
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
        <div className="space-x-2 flex items-start justify-end">
          {payerInfoError ? (
            <div className="flex space-x-2">
              <WarningFilled className="text-red-600 mt-1" />
              <span className="text-red-600">{payerInfoError}</span>
            </div>
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
