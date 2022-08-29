import { Form, Input } from 'antd';
import { useLazyGetDocumentFamilyByNameQuery } from '../document_family/documentFamilyApi';
import { DocDocumentLocation } from '../locations/types';
import { useAddDocumentFamilyMutation } from './documentFamilyApi';
import { Button, Modal } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { Rule } from 'antd/lib/form';
import { useEffect } from 'react';

interface DocumentFamilyCreateModalPropTypes {
  documentType: string;
  location: DocDocumentLocation | undefined;
  visible?: boolean;
  onClose: () => void;
  onSave: (documentFamilyId: string) => void;
}

export const DocumentFamilyCreateModal = (props: DocumentFamilyCreateModalPropTypes) => {
  const { documentType, location, visible, onClose, onSave } = props;
  const [form] = useForm();
  const [getDocumentFamilyByName] = useLazyGetDocumentFamilyByNameQuery();
  const [addDocumentFamily, { isLoading, data, isSuccess }] = useAddDocumentFamilyMutation();

  useEffect(() => {
    if (isSuccess && data) {
      onSave(data._id);
    }
  }, [isSuccess, data]);

  if (!location) {
    return <></>;
  }

  return (
    <>
      <Modal
        visible={visible}
        title={<>Add Document Family for {location.site_name}</>}
        width="50%"
        onCancel={() => {
          onClose();
        }}
        footer={[
          <Button onClick={onClose}>cancel</Button>,
          <Button type="primary" htmlType="submit" onClick={() => form.submit()}>
            Save
          </Button>,
        ]}
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
              <label>Site Name</label>
              <div>{location.site_name}</div>
            </div>

            <div className=" flex-1 mt-2 mb-4">
              <label>Document Type</label>
              <div>{documentType}</div>
            </div>
          </div>

          <h4>Document Family</h4>
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
        </Form>
      </Modal>
    </>
  );
};

// asyncValidator because rkt query makes this tough without hooks/dispatch
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
