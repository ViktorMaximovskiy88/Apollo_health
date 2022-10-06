import { useState } from 'react';
import { Form, Select, Button } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { DocDocument } from './types';
import { DocDocumentLocation } from './locations/types';
import { DocumentFamily } from './document_family/types';
import { DocumentFamilyCreateModal } from './document_family/LocationDocumentFamilyCreateModal';
import { useGetDocumentFamiliesQuery } from './document_family/documentFamilyApi';

interface DocDocumentLocationsPropTypes {
  docDocument: DocDocument;
  locations?: DocDocumentLocation[];
}

export const DocDocumentInfoFormFamilyField = ({
  docDocument,
  locations,
}: DocDocumentLocationsPropTypes) => {
  const form = Form.useFormInstance();
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const [selectedIndex, setSelectedLocationIndex] = useState<number>(-1);
  const { data = [] } = useGetDocumentFamiliesQuery({
    documentType: docDocument.document_type,
  });
  const options = data.map((item: DocumentFamily) => ({ value: item._id, label: item.name }));
  // const updatedLocation = Form.useWatch(['locations', index]);

  return (
    <div>
      <Form.Item label="Document Family" name="locations">
        <Select
          // value={updatedLocation?.document_family_id}
          // onSelect={(documentFamilyId: string) => {
          //   const locations = form.getFieldValue('locations');
          //   locations[index].document_family_id = documentFamilyId;
          //   form.setFieldsValue({ locations });
          // }}
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
        visible={isVisible}
        onSave={(documentFamilyId: string) => {
          const locations = form.getFieldValue('locations');
          locations[selectedIndex].document_family_id = documentFamilyId;
          form.setFieldsValue({ locations });
          setIsVisible(false);
          setSelectedLocationIndex(-1);
        }}
        onClose={() => {
          setIsVisible(false);
          setSelectedLocationIndex(-1);
        }}
      />
    </div>
  );
};
