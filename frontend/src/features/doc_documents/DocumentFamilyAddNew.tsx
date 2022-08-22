import { Form, Button, Modal } from 'antd';
import { useState } from 'react';
import { PlusOutlined } from '@ant-design/icons';
import { AddDocumentFamily } from './DocumentFamilyAddForm';
import { DocumentFamilyOption, DocumentFamilyType } from './types';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { useParams } from 'react-router-dom';
import { useAddDocumentFamilyMutation } from './documentFamilyApi';

const useModal = (): [boolean, () => void, () => void] => {
  const [isVisible, setIsVisible] = useState(false);

  const showModal = () => {
    setIsVisible(true);
  };

  const closeModal = () => {
    setIsVisible(false);
  };

  return [isVisible, showModal, closeModal];
};

const useAddDocumentFamily = () => {
  const [addDocumentFamilyFn] = useAddDocumentFamilyMutation();

  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  const docDocumentForm = Form.useFormInstance();
  const documentType = Form.useWatch('document_type', docDocumentForm);

  async function addDocumentFamily(documentFamily: DocumentFamilyType): Promise<string> {
    if (!doc) {
      throw new Error('DocDocument not found');
    }

    documentFamily.site_id = doc.site_id;
    documentFamily.document_type = documentType;

    const { _id } = await addDocumentFamilyFn(documentFamily).unwrap();
    return _id;
  }

  return addDocumentFamily;
};

const useSaveInSelect = () => {
  const docDocumentForm = Form.useFormInstance();

  const saveInSelect = (documentFamilyId: string): void => {
    docDocumentForm.setFieldsValue({
      document_family_id: documentFamilyId,
    });
  };

  return saveInSelect;
};

const Footer = ({ onCancel, isSaving }: { onCancel: () => void; isSaving: boolean }) => (
  <div className="ant-modal-footer mt-3">
    <Button onClick={onCancel}>Cancel</Button>
    <Button type="primary" htmlType="submit" loading={isSaving}>
      Submit
    </Button>
  </div>
);

export function AddNewDocumentFamilyButton({
  options,
  setOptions,
}: {
  options: DocumentFamilyOption[];
  setOptions: (options: DocumentFamilyOption[]) => void;
}) {
  const docDocumentForm = Form.useFormInstance();
  const { document_type, site_id } = docDocumentForm.getFieldsValue();
  const [isSaving, setIsSaving] = useState(false);
  const [isModalVisible, showModal, closeModal] = useModal();
  const addDocumentFamily = useAddDocumentFamily();
  const saveInSelect = useSaveInSelect();
  const [documentFamilyForm] = Form.useForm();

  const onFinish = async (documentFamily: DocumentFamilyType) => {
    setIsSaving(true);

    const documentFamilyId = await addDocumentFamily(documentFamily);
    saveInSelect(documentFamilyId);

    // so the document family name shows up in the Select immediately
    setOptions([...options, { value: documentFamilyId, label: documentFamily.name }]);

    documentFamilyForm.resetFields();
    closeModal();

    setIsSaving(false);
  };

  const onCancel = () => {
    documentFamilyForm.resetFields();
    closeModal();
  };

  return (
    <>
      <Modal
        visible={isModalVisible}
        onCancel={closeModal}
        title="Add Document Family"
        width="50%"
        okText="Submit"
        footer={null}
      >
        <AddDocumentFamily
          initialValues={{ document_type, site_id }}
          onFinish={onFinish}
          form={documentFamilyForm}
          isSaving={isSaving}
          lockSiteDocType
        >
          <Footer onCancel={onCancel} isSaving={isSaving} />
        </AddDocumentFamily>
      </Modal>

      <Button className="flex-1 my-7" type="dashed" onClick={showModal}>
        <PlusOutlined />
        Add New Document Family
      </Button>
    </>
  );
}
