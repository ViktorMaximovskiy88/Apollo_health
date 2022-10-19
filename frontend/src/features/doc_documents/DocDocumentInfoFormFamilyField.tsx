import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Form, Select, Button } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { DocumentFamily } from './document_family/types';
import { DocumentFamilyCreateModal } from './document_family/DocumentFamilyCreateModal';
import { useGetDocumentFamiliesQuery } from './document_family/documentFamilyApi';
import { useGetDocDocumentQuery } from './docDocumentApi';

interface DocDocumentLocationsPropTypes {
  onFieldChange: () => void;
}

export const DocDocumentInfoFormFamilyField = ({
  onFieldChange,
}: DocDocumentLocationsPropTypes) => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  const form = Form.useFormInstance();
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const { data } = useGetDocumentFamiliesQuery({
    documentType: doc?.document_type,
  });
  const options = data?.data.map((item: DocumentFamily) => ({ value: item._id, label: item.name }));
  options?.sort((a, b) => a.label.localeCompare(b.label));
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
          style={{ width: 'calc(100% - 96px)', marginRight: '8px' }}
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
        documentType={doc?.document_type}
        open={isVisible}
        onSave={(documentFamilyId: string) => {
          form.setFieldsValue({ document_family_id: documentFamilyId });
          onFieldChange();
          setIsVisible(false);
        }}
        onClose={() => {
          setIsVisible(false);
        }}
      />
    </div>
  );
};
