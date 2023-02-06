import { Button, Drawer, Form, Input, Popconfirm } from 'antd';
import { useLazyGetPayerFamiliesQuery, useLazyGetPayerFamilyByNameQuery } from './payerFamilyApi';
import { DocDocumentLocation } from '../doc_documents/locations/types';
import { useAddPayerFamilyMutation, useLazyConvertPayerFamilyDataQuery } from './payerFamilyApi';
import { useForm } from 'antd/lib/form/Form';
import { Rule } from 'antd/lib/form';
import { ReactNode, useCallback, useState } from 'react';
import { PayerFamily } from './types';
import { PayerFamilyInfoForm } from './PayerFamilyInfoForm';
import { CloseOutlined, WarningFilled } from '@ant-design/icons';
import { isErrorWithData } from '../../common/helpers';

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
  const [convertPayerFamily] = useLazyConvertPayerFamilyDataQuery();
  const [payerInfoError, setPayerInfoError] = useState<ReactNode>();
  const [popupOpen, setPopupOpen] = useState(false);

  const handleClose = useCallback(() => {
    props.onClose();
    setPayerInfoError('');
    form.resetFields();
  }, [form, props]);

  const onFinish = useCallback(
    async (values: Partial<PayerFamily>) => {
      try {
        const payerFamily = await addPayerFamily(values).unwrap();
        onSave(payerFamily);
        form.resetFields();
      } catch (err: any) {
        if (isErrorWithData(err)) {
          setPayerInfoError(err.data.detail);
        } else {
          setPayerInfoError('Error Creating A New Payer Family');
        }
      }
    },
    [addPayerFamily, onSave, form]
  );

  const [queryPf] = useLazyGetPayerFamiliesQuery();
  const onSubmit = useCallback(
    async (e: any, confirmed: boolean = false) => {
      await form.validateFields();

      const { name, payer_type, payer_ids, channels, benefits, plan_types, regions } =
        form.getFieldsValue(true);
      if (
        !payer_ids.length &&
        !channels.length &&
        !benefits.length &&
        !plan_types.length &&
        !regions.length
      ) {
        setPayerInfoError('At least one payer value is required');
        return;
      }
      if (!payer_ids.length && !confirmed) {
        setPopupOpen(true);
        return;
      }
      try {
        const { data: existingPfs } = await queryPf({
          limit: 1,
          filterValue: [
            { name: 'payer_type', value: payer_type, type: 'string', operator: 'eq' },
            { name: 'payer_ids', value: payer_ids, type: 'string', operator: 'leq' },
            { name: 'plan_types', value: plan_types, type: 'string', operator: 'leq' },
            { name: 'regions', value: regions, type: 'string', operator: 'leq' },
            { name: 'channels', value: channels, type: 'string', operator: 'leq' },
            { name: 'benefits', value: benefits, type: 'string', operator: 'leq' },
          ],
        }).unwrap();
        const existingPf = existingPfs[0];
        if (existingPf) {
          const onSwitchToExisting = async () => {
            onSave(existingPf);
            handleClose();
          };
          const message = (
            <>
              <div>Payer Family '{existingPf.name}' already matches this criteria.</div>
              {location?.site_name ? (
                <div>
                  Click <a onClick={onSwitchToExisting}>here</a> to select it instead.
                </div>
              ) : null}
            </>
          );
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
      setPopupOpen(false);
    },
    [form]
  );

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
          payer_type: 'Not Selected',
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

        <div className="space-x-2 flex items-start justify-end">
          {payerInfoError ? (
            <div className="flex space-x-2">
              <WarningFilled className="text-red-600 mt-1" />
              <span className="text-red-600">{payerInfoError}</span>
            </div>
          ) : null}

          <Button onClick={handleClose}>Cancel</Button>
          <Popconfirm
            title="No backbone value selected"
            open={popupOpen}
            okText="Save"
            cancelText="Cancel"
            onConfirm={(e) => onSubmit(e, true)}
            onCancel={() => setPopupOpen(false)}
          >
            <Button type="primary" onClick={onSubmit} loading={isLoading}>
              Submit
            </Button>
          </Popconfirm>
        </div>
      </Form>
    </Drawer>
  );
};

// asyncValidator because rtk query makes this tough without hooks/dispatch
export function mustBeUniqueName(asyncValidator: Function) {
  return {
    async validator(_rule: Rule, value: string) {
      let payerFamily;
      if (value) {
        let { data } = await asyncValidator({ name: value });
        payerFamily = data;
      } else {
        return Promise.reject();
      }
      if (payerFamily) {
        return Promise.reject(`Payer family name "${payerFamily.name}" already exists`);
      }
      return Promise.resolve();
    },
  };
}
