import { useState } from 'react';
import { Form } from 'antd';
import { DocDocument } from '../types';
import { DocDocumentLocation } from './types';
import { DocDocumentLocationForm } from '../../payer-family/DocDocumentLocationForm';
import { PayerFamilyCreateModal } from '../../payer-family/LocationPayerFamilyCreateModal';
import { PayerFamilyEditModal } from '../../payer-family/LocationPayerFamilyEditModal';

interface DocDocumentLocationsPropTypes {
  docDocument: DocDocument;
  locations: DocDocumentLocation[];
}

export const DocDocumentLocations = ({ docDocument, locations }: DocDocumentLocationsPropTypes) => {
  const form = Form.useFormInstance();
  const [editModalOpen, setEditModalOpen] = useState<boolean>(false);
  const [createModalOpen, setCreateModalOpen] = useState<boolean>(false);
  const [editPayerFamilyId, setEditPayerFamilyId] = useState<string>('');
  const [selectedIndex, setSelectedLocationIndex] = useState<number>(-1);

  return (
    <div>
      {locations.map((location, index) => (
        <DocDocumentLocationForm
          key={location.site_id}
          index={index}
          documentType={docDocument.document_type}
          location={location}
          setEditPayerFamilyId={setEditPayerFamilyId}
          onShowPayerFamilyCreate={() => {
            setSelectedLocationIndex(index);
            setCreateModalOpen(true);
          }}
          onShowPayerFamilyEdit={() => {
            setSelectedLocationIndex(index);
            setEditModalOpen(true);
          }}
        />
      ))}
      {createModalOpen ? (
        <PayerFamilyCreateModal
          location={locations[selectedIndex]}
          open={createModalOpen}
          onSave={(payerFamilyId: string) => {
            form.setFieldValue(['locations', selectedIndex, 'payer_family_id'], payerFamilyId);
            setCreateModalOpen(false);
            setEditPayerFamilyId(payerFamilyId);
            setSelectedLocationIndex(-1);
          }}
          onClose={() => {
            setCreateModalOpen(false);
            setSelectedLocationIndex(-1);
          }}
        />
      ) : null}

      {editModalOpen ? (
        <PayerFamilyEditModal
          location={locations[selectedIndex]}
          payer_family_id={editPayerFamilyId}
          open={editModalOpen}
          onSave={(payerFamilyId: string) => {
            form.setFieldValue(['locations', selectedIndex, 'payer_family_id'], payerFamilyId);
            setEditModalOpen(false);
            setSelectedLocationIndex(-1);
          }}
          onClose={() => {
            setEditModalOpen(false);
            setSelectedLocationIndex(-1);
          }}
        />
      ) : null}
    </div>
  );
};
