import { Button, Drawer, Form, Input } from 'antd';
import { useLazyGetPayerFamilyByNameQuery } from './payerFamilyApi';
import { DocDocumentLocation } from '../doc_documents/locations/types';
import { useAddPayerFamilyMutation } from './payerFamilyApi';
import { useLazyGetPayerBackboneByLIdQuery } from '../payer-backbone/payerBackboneApi';
import { useForm } from 'antd/lib/form/Form';
import { Rule } from 'antd/lib/form';
import { useCallback, useState } from 'react';
import { PayerFamily } from './types';
import { PayerFamilyInfoForm } from './PayerFamilyInfoForm';
import { CloseOutlined, WarningFilled } from '@ant-design/icons';

interface PayerFamilyCreateDrawerPropTypes {
  location: DocDocumentLocation | undefined;
  open?: boolean;
  onClose: () => void;
  onSave: (newPayerFamily: PayerFamily) => void;
}

export const PayerFamilyCreateDrawer = (props: PayerFamilyCreateDrawerPropTypes) => {
  const { location, onClose, onSave, open } = props;
  const [form] = useForm();
  const [getPayerFamilyByName] = useLazyGetPayerFamilyByNameQuery();
  const [getPayerName] = useLazyGetPayerBackboneByLIdQuery();

  const [addPayerFamily, { isLoading }] = useAddPayerFamilyMutation();
  const [payerInfoError, setPayerInfoError] = useState<boolean>(false);

  const onFinish = useCallback(
    async (values: Partial<PayerFamily>) => {
      const payerFamily = await addPayerFamily(values).unwrap();
      onSave(payerFamily);
      form.resetFields();
    },
    [addPayerFamily, onSave, form]
  );

  const onSubmit = useCallback(async () => {
    let { payer_type, payer_ids, channels, benefits, plan_types, regions } =
      form.getFieldsValue(true);
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
    let getPayerNameVals = async () => {
      const payers: any = [];
      for (let i = 0; i < payer_ids.length; i++) {
        const { data } = await getPayerName({ payerType: payer_type, id: payer_ids[i] });
        payers.push(data?.name);
      }
      return payers;
    };
    let payerNames;
    if (payer_ids && payer_ids[0] !== '') {
      payerNames = await getPayerNameVals();
    }
    const newName = [regions, plan_types, benefits, channels, payerNames]
      .filter((vals: any) => (!vals || vals.length === 0 ? false : true))
      .join(' | ');
    form.setFieldsValue({ name: newName });
    form.submit();
  }, [form, getPayerName]);

  if (!location) {
    return <></>;
  }

  return (
    <Drawer
      open={open}
      title={<>Add Payer Family for {location.site_name}</>}
      width="30%"
      placement="left"
      closable={false}
      mask={false}
      extra={
        <Button type="text" onClick={onClose}>
          <CloseOutlined />
        </Button>
      }
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
        <div className="flex">
          <div className="flex-1 mt-2 mb-4">
            <h3>Site</h3>
            <div>{location.site_name}</div>
          </div>
        </div>
        <Input.Group className="space-x-2 flex">
          <Form.Item
            label="Name"
            name="name"
            className="w-96 mr-5"
            rules={[
              { required: false, message: 'Please input a payer family name' },
              mustBeUnique(getPayerFamilyByName),
            ]}
          >
            <Input disabled={true} placeholder={'Custom Name will be generated'} />
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
function mustBeUnique(asyncValidator: Function) {
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