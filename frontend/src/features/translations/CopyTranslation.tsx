import { Form, Input, Spin } from 'antd';
import { Modal } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { Rule } from 'antd/lib/form';
import { useState } from 'react';
import { CopyOutlined } from '@ant-design/icons';
import { Tooltip } from 'antd';
import { ButtonLink } from '../../components';
import {
  useAddTranslationConfigMutation,
  useLazyGetTranslationConfigByNameQuery,
} from './translationApi';
import { TranslationConfig } from './types';
import { useNavigate } from 'react-router-dom';

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

export const CopyTranslation = ({ translation }: { translation: TranslationConfig }) => {
  const [visible, setVisible] = useState(false);
  const [form] = useForm();
  const navigate = useNavigate();

  const [getTranslationByName, { isFetching: validatorLoading }] =
    useLazyGetTranslationConfigByNameQuery();

  const [addTranslation, { isLoading: addTranslationLoading }] = useAddTranslationConfigMutation();

  const handleCancel = () => {
    setVisible(false);
    form.resetFields();
  };

  const handleFinish = async ({ name }: { name: string }) => {
    setVisible(false);
    const newTranslation = await addTranslation({
      ...translation,
      name,
      _id: undefined,
    }).unwrap();
    navigate(`./${newTranslation._id}`);
  };

  const isLoading = validatorLoading || addTranslationLoading;

  return (
    <>
      <Tooltip title="Copy Translation">
        <ButtonLink onClick={() => setVisible(true)}>
          <CopyOutlined />
        </ButtonLink>
      </Tooltip>
      <Modal
        visible={visible}
        title={
          <>
            Copy Translation of "{translation.name}" <Spin spinning={isLoading} />
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
};
