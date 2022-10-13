import { useState } from 'react';
import { Form, Select, Button } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { DocDocument } from './types';
import { DocumentFamily } from './document_family/types';
import { DocumentFamilyCreateModal } from './document_family/DocumentFamilyCreateModal';
import { useGetDocumentFamiliesQuery } from './document_family/documentFamilyApi';

interface DocDocumentLocationsPropTypes {
  docDocument: DocDocument;
  onFieldChange: () => void;
}

export const DocDocumentInfoFormFamilyField = ({
  docDocument,
  onFieldChange,
}: DocDocumentLocationsPropTypes) => {
  const form = Form.useFormInstance();
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const [selectedIndex, setSelectedLocationIndex] = useState<number>(-1);
  const { data } = useGetDocumentFamiliesQuery({
    documentType: docDocument.document_type,
  });
  const options = data?.data.map((item: DocumentFamily) => ({ value: item._id, label: item.name }));
  const document_family_id = Form.useWatch('document_family_id');
  return (
    <div>
      <Form.Item label="Document Family" name="document_family_id">
        <Select
          value={document_family_id}
          onSelect={(documentFamilyId: string) => {
            form.setFieldsValue({ document_family_id: documentFamilyId });
            onFieldChange();
          }}
          options={options}
          style={{ width: 'calc(100% - 96px', marginRight: '8px' }}
        />
        <Button
          type="dashed"
          onClick={() => {
            setIsVisible(true);
          }}
        >
          <PlusOutlined />
          New
        </Button>
      </Form.Item>

      <DocumentFamilyCreateModal
        documentType={docDocument.document_type}
        open={isVisible}
        onSave={(documentFamilyId: string) => {
          setIsVisible(false);
        }}
        onClose={() => {
          setIsVisible(false);
          setSelectedLocationIndex(-1);
        }}
      />
    </div>
  );
};
