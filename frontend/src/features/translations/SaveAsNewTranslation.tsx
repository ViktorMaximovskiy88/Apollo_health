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
  const [visible, setOpen] = useState<boolean>(false);
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
      setOpen(true);
      return;
    }
    const values = editTranslationForm.getFieldsValue();
    const newTranslation = await addTranslation({
      ...values,
      _id: undefined,
    }).unwrap();

    navigate(`../${newTranslation._id}`);
  };

  const handleCancel = () => {
    setOpen(false);
    modalForm.resetFields();
  };

  const handleFinish = async ({ name }: { name: string }) => {
    const values = editTranslationForm.getFieldsValue();
    const newTranslation = await addTranslation({
      ...values,
      name,
      _id: undefined,
    }).unwrap();

    navigate(`../${newTranslation._id}`);
    editTranslationForm.setFieldsValue({ name }); // does not update name without
    setOpen(false);
  };

  const isLoading = validatorLoading || addTranslationLoading;

  return (
    <>
      <Button onClick={handleSaveAsClick} loading={validatorLoading}>
        Save As New
      </Button>
      <Modal
        open={visible}
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
