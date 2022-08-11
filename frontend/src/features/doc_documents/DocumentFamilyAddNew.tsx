import { Form, Button } from 'antd';
import { createContext, useState } from 'react';
import { PlusOutlined } from '@ant-design/icons';
import { AddDocumentFamily as AddDocumentFamilyModal } from './DocumentFamilyAddForm';
import { FormInstance } from 'antd/lib/form';
import { DocumentFamilyOption } from './types';

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

export const DocDocumentFormContext = createContext<FormInstance>({} as FormInstance);

export function AddNewDocumentFamilyButton({
  options,
  setOptions,
}: {
  options: DocumentFamilyOption[];
  setOptions: (options: DocumentFamilyOption[]) => void;
}) {
  const form = Form.useFormInstance();
  const [isModalVisible, showModal, closeModal] = useModal();

  return (
    <>
      <DocDocumentFormContext.Provider value={form}>
        <AddDocumentFamilyModal
          closeModal={closeModal}
          visible={isModalVisible}
          options={options}
          setOptions={setOptions}
        />
      </DocDocumentFormContext.Provider>

      <Button className="flex-1 my-7" type="dashed" onClick={showModal}>
        <PlusOutlined />
        Add New Document Family
      </Button>
    </>
  );
}
