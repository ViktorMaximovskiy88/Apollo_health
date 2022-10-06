import { Form, Input, Select } from 'antd';
import { useLazyGetDocumentFamilyByNameQuery } from './documentFamilyApi';
import { DocDocumentLocation } from '../locations/types';
import { useAddDocumentFamilyMutation } from './documentFamilyApi';
import { Modal } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { Rule } from 'antd/lib/form';
import { useCallback, useEffect } from 'react';
import { RemoteSelect } from '../../../components';
import { useLazyGetPayerBackbonesQuery } from '../../payer-backbone/payerBackboneApi';
import {
  payerTypeOptions,
  channelOptions,
  benefitOptions,
  planTypeOptions,
  regionOptions,
  fieldGroupsOptions,
} from './payerLevels';

interface DocumentFamilyCreateModalPropTypes {
  documentType: string;
  location?: DocDocumentLocation | undefined;
  visible?: boolean;
  onClose: () => void;
  onSave: (documentFamilyId: string) => void;
}

function PayerInfo() {
  const [getPayers] = useLazyGetPayerBackbonesQuery();
  const form = Form.useFormInstance();
  const payerType = Form.useWatch(['payer_info', 'payer_type']);

  useEffect(() => {
    form.setFieldsValue({ payer_info: { payer_ids: [] } });
  }, [form, payerType]);

  const payerOptions = useCallback(
    async (search: string) => {
      if (!payerType) return [];
      const { data } = await getPayers({
        type: payerType,
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [{ name: 'name', operator: 'contains', type: 'string', value: search }],
      });
      if (!data) return [];
      return data.data.map((payer) => ({ label: payer.name, value: payer.l_id }));
    },
    [getPayers, payerType]
  );

  return (
    <div className="mt-4">
      <h2>Payer</h2>
      <Input.Group className="space-x-2 flex">
        <Form.Item label="Payer Type" name={['payer_info', 'payer_type']} className="w-48">
          <Select options={payerTypeOptions} />
        </Form.Item>
        <Form.Item label="Payers" name={['payer_info', 'payer_ids']} className="grow">
          <RemoteSelect mode="multiple" className="w-full" fetchOptions={payerOptions} />
        </Form.Item>
      </Input.Group>
      <Input.Group className="space-x-2 flex">
        <Form.Item label="Channel" name={['payer_info', 'channels']} className="w-full">
          <Select mode="multiple" options={channelOptions} />
        </Form.Item>
        <Form.Item label="Benefit" name={['payer_info', 'benefits']} className="w-full">
          <Select mode="multiple" options={benefitOptions} />
        </Form.Item>
        <Form.Item label="Plan Types" name={['payer_info', 'plan_types']} className="w-full">
          <Select mode="multiple" options={planTypeOptions} />
        </Form.Item>
        <Form.Item label="Region" name={['payer_info', 'regions']} className="w-full">
          <Select mode="multiple" options={regionOptions} />
        </Form.Item>
      </Input.Group>
    </div>
  );
}

export const DocumentFamilyCreateModal = (props: DocumentFamilyCreateModalPropTypes) => {
  let legacyRelevanceOptions = [
    { label: 'Editor Manual', value: 'EDITOR_MANUAL' },
    { label: 'Editor Automated ', value: 'EDITOR_AUTOMATED' },
    { label: 'PAR', value: 'PAR' },
    { label: 'N/A', value: 'N/A' },
  ];
  const { documentType, location, visible, onClose, onSave } = props;
  const [form] = useForm();
  const [getDocumentFamilyByName] = useLazyGetDocumentFamilyByNameQuery();
  const [addDocumentFamily, { isLoading, data, isSuccess }] = useAddDocumentFamilyMutation();
  const nameValue: string[] = Form.useWatch('legacy_relevance', form);
  let filteredlegacyRelevanceOptions = legacyRelevanceOptions;

  if (nameValue?.includes('N/A')) {
    filteredlegacyRelevanceOptions = legacyRelevanceOptions.map((e) => {
      if (e.value === 'N/A') return e;
      return { ...e, disabled: true };
    });
  } else if (
    nameValue?.includes('PAR') ||
    nameValue?.includes('EDITOR_MANUAL') ||
    nameValue?.includes('EDITOR_AUTOMATED')
  ) {
    filteredlegacyRelevanceOptions = legacyRelevanceOptions.map((e) => {
      if (e.value === 'N/A') {
        return { ...e, disabled: true };
      } else if (
        (nameValue?.includes('EDITOR_MANUAL') && e.value == 'EDITOR_AUTOMATED') ||
        (nameValue?.includes('EDITOR_AUTOMATED') && e.value == 'EDITOR_MANUAL')
      ) {
        return { ...e, disabled: true };
      }
      return e;
    });
  }

  useEffect(() => {
    if (isSuccess && data) {
      onSave(data._id);
      form.resetFields();
    }
  }, [isSuccess, data]);

  if (!location) {
    return <></>;
  }

  return (
    <Modal
      visible={visible}
      title={<>Add Document Family for {location.site_name}</>}
      width="50%"
      okText="Submit"
      onOk={form.submit}
      onCancel={onClose}
    >
      <Form
        form={form}
        layout="vertical"
        disabled={isLoading}
        autoComplete="off"
        requiredMark={false}
        validateTrigger={['onBlur']}
        onFinish={(values: any) => {
          addDocumentFamily({
            ...values,
            site_id: location.site_id,
            document_type: documentType,
          });
        }}
      >
        <div className="flex">
          <div className="flex-1 mt-2 mb-4">
            <h3>Site</h3>
            <div>{location.site_name}</div>
          </div>

          <div className="flex-1 mt-2 mb-4">
            <h3>Document Type</h3>
            <div>{documentType}</div>
          </div>
        </div>
        <Form.Item
          label="Name"
          name="name"
          rules={[
            { required: true, message: 'Please input a document family name' },
            mustBeUniqueToSite(location.site_id, getDocumentFamilyByName),
          ]}
        >
          <Input />
        </Form.Item>
        <Input.Group className="space-x-2 flex">
          <Form.Item label="Legacy Relevance" name="legacy_relevance" className="w-full">
            <Select mode="multiple" options={filteredlegacyRelevanceOptions} />
          </Form.Item>

          <Form.Item label="Field Groups" name="field_groups" className="w-full">
            <Select mode="multiple" options={fieldGroupsOptions} />
          </Form.Item>
        </Input.Group>
      </Form>
    </Modal>
  );
};

// asyncValidator because rtk query makes this tough without hooks/dispatch
function mustBeUniqueToSite(siteId: string, asyncValidator: Function) {
  return {
    async validator(_rule: Rule, value: string) {
      const { data: documentFamily } = await asyncValidator({ name: value, siteId });
      if (documentFamily) {
        return Promise.reject(
          `Document family name "${documentFamily.name}" already exists on this site`
        );
      }
      return Promise.resolve();
    },
  };
}
