import { Button, Form, FormInstance, Input, Modal, Spin } from 'antd';
import { Rule } from 'antd/lib/form';
import { useForm } from 'antd/lib/form/Form';
import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  useAddTranslationConfigMutation,
  useGetTranslationConfigQuery,
  useLazyGetTranslationConfigByNameQuery,
} from './translationApi';

const nameMustBeUnique = (getTranslationByName: any) => {
  return {
    // See https://ant.design/components/form/#Rule
    async validator(_rule: Rule, name: string) {
      const { data: translation } = await getTranslationByName(name);
      if (translation) {
        return Promise.reject(`Translation name "${name}" already exists`);
      }
      return Promise.resolve();
    },
  };
};

// Component uses a modal because changing validation in the form depending on which button is clicked would be difficult
export function SaveAsNew({ form: editTranslationForm }: { form: FormInstance<any> }) {
  const [modalForm] = useForm();
  const { translationId } = useParams();
  const { data: translation } = useGetTranslationConfigQuery(translationId);
  const [visible, setVisible] = useState<boolean>(false);
  const [getTranslationByName, { isFetching: validatorLoading }] =
    useLazyGetTranslationConfigByNameQuery();
  const [addTranslation, { isLoading: addTranslationLoading }] = useAddTranslationConfigMutation();
  const navigate = useNavigate();

  if (!translation) return null;

  const getIsTranslationNameUnique = async (name: string): Promise<boolean> => {
    const { data: translation } = await getTranslationByName(name);
    return !translation;
  };
  const handleSaveAsClick = async () => {
    const isTranslationNameUnique = await getIsTranslationNameUnique(
      editTranslationForm.getFieldValue('name')
    );
    if (!isTranslationNameUnique) {
      setVisible(true);
      return;
    }
    const values = editTranslationForm.getFieldsValue();
    const response = await addTranslation({
      ...values,
      _id: undefined,
    });

    // resolves TS error
    if ('error' in response) {
      console.error(response.error);
      throw new Error('Tried to add a new translation but recieved an error in response');
    }

    const { data: newTranslation } = response;
    navigate(`../${newTranslation._id}`);
  };

  const handleCancel = () => {
    setVisible(false);
    modalForm.resetFields();
  };

  const handleFinish = async ({ name }: { name: string }) => {
    const values = editTranslationForm.getFieldsValue();
    const response = await addTranslation({
      ...values,
      name,
      _id: undefined,
    });

    // resolves TS error
    if ('error' in response) {
      console.error(response.error);
      throw new Error('Tried to add a new translation but recieved an error in response');
    }

    const { data: newTranslation } = response;
    navigate(`../${newTranslation._id}`);
    editTranslationForm.setFieldsValue({ name }); // does not update name without
    setVisible(false);
  };

  const isLoading = validatorLoading || addTranslationLoading;

  return (
    <>
      <Button
        onClick={handleSaveAsClick}
        style={{ color: 'white', backgroundColor: '#6C757D' }} // TODO: refactor to use type prop or classname
        loading={validatorLoading}
      >
        Save As New
      </Button>
      <Modal
        visible={visible}
        title={
          <>
            Save As New: Name "{editTranslationForm.getFieldValue('name')}" is not unique
            <Spin spinning={isLoading} />
          </>
        }
        width="50%"
        okText="Submit"
        onOk={modalForm.submit}
        onCancel={handleCancel}
      >
        <Form
          form={modalForm}
          layout="vertical"
          disabled={isLoading}
          autoComplete="off"
          requiredMark={false}
          validateTrigger={['onBlur']}
          onFinish={handleFinish}
          initialValues={translation}
        >
          <Form.Item
            label="Name"
            name="name"
            rules={[
              { required: true, message: 'Please input a translation name' },
              nameMustBeUnique(getTranslationByName),
            ]}
          >
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
