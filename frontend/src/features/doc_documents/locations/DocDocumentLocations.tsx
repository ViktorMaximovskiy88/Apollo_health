import { useState } from 'react';
import { Form } from 'antd';
import { DocDocument } from '../types';
import { DocDocumentLocation } from './types';
import { DocDocumentLocationForm } from './DocDocumentLocationForm';
import { DocumentFamilyCreateModal } from '../document_family/LocationDocumentFamilyCreateModal';

interface DocDocumentLocationsPropTypes {
  docDocument: DocDocument;
  locations: DocDocumentLocation[];
}

export const DocDocumentLocations = ({ docDocument, locations }: DocDocumentLocationsPropTypes) => {
  const form = Form.useFormInstance();
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const [selectedIndex, setSelectedLocationIndex] = useState<number>(-1);

  return (
    <div>
      {locations.map((location, index) => (
        <>
          <DocDocumentLocationForm
            key={location.site_id}
            index={index}
            documentType={docDocument.document_type}
            location={location}
            onShowDocumentFamilyCreate={() => {
              setSelectedLocationIndex(index);
              setIsVisible(true);
            }}
          />
        </>
      ))}

      <DocumentFamilyCreateModal
        location={locations[selectedIndex]}
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
