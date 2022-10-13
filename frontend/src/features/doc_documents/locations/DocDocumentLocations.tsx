import { useState } from 'react';
import { Form } from 'antd';
import { DocDocument } from '../types';
import { DocDocumentLocation } from './types';
import { DocDocumentLocationForm } from '../../payer-family/DocDocumentLocationForm';
import { PayerFamilyCreateModal } from '../../payer-family/LocationPayerFamilyCreateModal';

interface DocDocumentLocationsPropTypes {
  docDocument: DocDocument;
  locations: DocDocumentLocation[];
}

export const DocDocumentLocations = ({ docDocument, locations }: DocDocumentLocationsPropTypes) => {
  const form = Form.useFormInstance();
  const [modalOpen, setModalOpen] = useState<boolean>(false);
  const [selectedIndex, setSelectedLocationIndex] = useState<number>(-1);

  return (
    <div>
      {locations.map((location, index) => (
        <DocDocumentLocationForm
          key={location.site_id}
          index={index}
          documentType={docDocument.document_type}
          location={location}
          onShowPayerFamilyCreate={() => {
            setSelectedLocationIndex(index);
            setModalOpen(true);
          }}
        />
      ))}

      <PayerFamilyCreateModal
        location={locations[selectedIndex]}
        documentType={docDocument.document_type}
        open={modalOpen}
        onSave={(documentFamilyId: string) => {
          const locations = form.getFieldValue('locations');
          locations[selectedIndex].document_family_id = documentFamilyId;
          form.setFieldsValue({ locations });
          setModalOpen(false);
          setSelectedLocationIndex(-1);
        }}
        onClose={() => {
          setModalOpen(false);
          setSelectedLocationIndex(-1);
        }}
      />
    </div>
  );
};
