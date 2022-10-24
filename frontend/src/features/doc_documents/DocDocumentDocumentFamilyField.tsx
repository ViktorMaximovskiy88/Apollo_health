import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Form, Select, Button } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';
import { DocumentFamily } from './document_family/types';
import { DocumentFamilyCreateModal } from './document_family/DocumentFamilyCreateModal';
import {
  useGetDocumentFamiliesQuery,
  useGetDocumentFamilyQuery,
} from './document_family/documentFamilyApi';
import { useGetDocDocumentQuery } from './docDocumentApi';

interface DocDocumentLocationsPropTypes {
  onFieldChange: () => void;
}

export const DocDocumentDocumentFamilyField = ({
  onFieldChange,
}: DocDocumentLocationsPropTypes) => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  const form = Form.useFormInstance();
  const [isNewVisible, setIsNewVisible] = useState<boolean>(false);
  const [isEditVisible, setIsEditVisible] = useState<boolean>(false);
  const [skip, setSkip] = useState<boolean>(true);
  const { data } = useGetDocumentFamiliesQuery({
    documentType: doc?.document_type,
  });
  const options = data?.data.map((item: DocumentFamily) => ({ value: item._id, label: item.name }));
  options?.sort((a: { label: string }, b: { label: string }) => a.label.localeCompare(b.label));
  const document_family_id = Form.useWatch('document_family_id');

  const [docFamilyData, setDocFamilyData] = useState<any>(undefined);
  let { data: docFamData } = useGetDocumentFamilyQuery(document_family_id, { skip });

  useEffect(() => {
    if (document_family_id) {
      setSkip(false);
      setDocFamilyData(docFamData);
    }
  }, [document_family_id, docFamData]);

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
          style={
            document_family_id
              ? { width: 'calc(100% - 190px)', marginRight: '8px' }
              : { width: 'calc(100% - 96px)', marginRight: '8px' }
          }
        />
        {document_family_id && (
          <Button
            type="dashed"
            className="mr-2"
            onClick={() => {
              setIsEditVisible(true);
            }}
          >
            <EditOutlined />
            Edit
          </Button>
        )}
        <DocumentFamilyCreateModal
          documentFamilyData={docFamilyData}
          documentType={doc?.document_type}
          open={isEditVisible}
          onSave={(documentFamilyId: string) => {
            onFieldChange();
            setIsEditVisible(false);
          }}
          onClose={() => {
            setIsEditVisible(false);
          }}
        />

        <Button
          type="dashed"
          onClick={() => {
            setIsNewVisible(true);
          }}
        >
          <PlusOutlined />
          New
        </Button>
        <DocumentFamilyCreateModal
          documentType={doc?.document_type}
          open={isNewVisible}
          onSave={(documentFamilyId: string) => {
            form.setFieldsValue({ document_family_id: documentFamilyId });
            onFieldChange();
            setIsNewVisible(false);
          }}
          onClose={() => {
            setIsNewVisible(false);
          }}
        />
      </Form.Item>
    </div>
  );
};
