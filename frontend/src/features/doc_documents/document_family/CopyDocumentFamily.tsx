import { Form, Input, Spin } from 'antd';
import { Modal } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { Rule } from 'antd/lib/form';
import { useState } from 'react';
import { CopyOutlined } from '@ant-design/icons';
import { Tooltip } from 'antd';
import { ButtonLink } from '../../../components';
import {
  useAddDocumentFamilyMutation,
  useLazyGetDocumentFamilyByNameQuery,
} from './documentFamilyApi';
import { DocumentFamily } from './types';
import { useNavigate } from 'react-router-dom';

const nameMustBeUnique = (getDocumentFamilyByName: any) => {
  return {
    // See https://ant.design/components/form/#Rule
    async validator(_rule: Rule, name: string) {
      const { data: documentFamily } = await getDocumentFamilyByName({ name });
      if (documentFamily) {
        return Promise.reject(`DocumentFamily name "${name}" already exists`);
      }
      return Promise.resolve();
    },
  };
};

export const CopyDocumentFamily = ({ documentFamily }: { documentFamily: DocumentFamily }) => {
  const [visible, setOpen] = useState(false);
  const [form] = useForm();
  const navigate = useNavigate();

  const [getDocumentFamilyByName, { isFetching: validatorLoading }] =
    useLazyGetDocumentFamilyByNameQuery();

  const [addDocumentFamily, { isLoading: addDocumentFamilyLoading }] =
    useAddDocumentFamilyMutation();

  const handleCancel = () => {
    setOpen(false);
    form.resetFields();
  };

  const handleFinish = async ({ name }: { name: string }) => {
    setOpen(false);
    const newDocumentFamily = await addDocumentFamily({
      ...documentFamily,
      name,
      _id: undefined,
    }).unwrap();
    navigate(`./${newDocumentFamily._id}`);
  };

  const isLoading = validatorLoading || addDocumentFamilyLoading;

  return (
    <>
      <Tooltip title="Copy Document Family">
        <ButtonLink onClick={() => setOpen(true)}>
          <CopyOutlined />
        </ButtonLink>
      </Tooltip>
      <Modal
        open={visible}
        title={
          <>
            Copy Document Family of "{documentFamily.name}" <Spin spinning={isLoading} />
          </>
        }
        width="50%"
        okText="Submit"
        onOk={form.submit}
        onCancel={handleCancel}
      >
        <Form
          form={form}
          layout="vertical"
          disabled={isLoading}
          autoComplete="off"
          requiredMark={false}
          validateTrigger={['onBlur']}
          onFinish={handleFinish}
          initialValues={documentFamily}
        >
          <Form.Item
            label="Name"
            name="name"
            rules={[
              { required: true, message: 'Please input a document family name' },
              nameMustBeUnique(getDocumentFamilyByName),
            ]}
          >
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};
