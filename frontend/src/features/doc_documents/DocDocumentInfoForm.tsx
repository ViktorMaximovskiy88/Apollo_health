import { Form, Input, FormInstance, Select, Button, Modal } from 'antd';
import { Hr } from '../../components';
import { DocDocument } from './types';
import { DateFields } from './DocDocumentDateFields';
import { DocumentClassification } from './DocDocumentClassificationFields';
import { ExtractionFields } from './DocDocumentExtractionFields';
import { UrlFields } from './DocDocumentUrlFields';
import { PlusOutlined } from '@ant-design/icons';
import { useState } from 'react';

const { Option } = Select;

const Name = () => (
  <Form.Item name="name" label="Name" required={true}>
    <Input />
  </Form.Item>
);

interface ModalPropTypes {
  onOk: () => void;
  onCancel: () => void;
}
const useModal = (): [boolean, () => void, ModalPropTypes] => {
  const [isVisible, setIsVisible] = useState(false);

  const showModal = () => {
    setIsVisible(true);
  };

  const onOk = () => {
    setIsVisible(false);
  };

  const onCancel = () => {
    setIsVisible(false);
  };

  const modalProps = { onOk, onCancel };

  return [isVisible, showModal, modalProps];
};

const DocumentFamily = () => {
  const children = [];

  for (let i = 10; i < 36; i++) {
    children.push({ key: i.toString(36) + i, label: i.toString(36) + i });
  }
  const [options, setOptions] = useState(children);

  const [isModalVisible, showModal, modalProps] = useModal();

  return (
    <div className="flex space-x-8">
      <Modal {...modalProps} visible={isModalVisible} />
      <Form.Item name="document_family" label="Document Family" className="flex-1">
        <Select mode="multiple" allowClear placeholder="None selected" defaultValue={[]}>
          {options.map(({ key, label }) => (
            <Option key={key}>{label}</Option>
          ))}
        </Select>
      </Form.Item>
      <Button className="flex-1 my-7" type="dashed" onClick={showModal}>
        <PlusOutlined />
        Add New Document Family
      </Button>
    </div>
  );
};

export function DocDocumentInfoForm(props: {
  doc: DocDocument;
  form: FormInstance;
  onFieldChange: Function;
}) {
  const { doc } = props;
  return (
    <>
      <Name />
      <Hr />
      <DocumentClassification doc={doc} />
      <Hr />
      <DocumentFamily />
      <Hr />
      <DateFields {...props} />
      <Hr />
      <ExtractionFields doc={doc} />
      <Hr />
      <UrlFields doc={doc} />
    </>
  );
}
