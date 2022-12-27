import { useState } from 'react';
import { Form } from 'antd';
import { DocDocumentLocation } from './types';
import { DocDocumentLocationForm } from '../../payer-family/DocDocumentLocationForm';
import { PayerFamilyCreateDrawer } from '../../payer-family/LocationPayerFamilyCreateDrawer';
import { PayerFamilyEditDrawer } from '../../payer-family/LocationPayerFamilyEditDrawer';
import { PayerFamily } from '../../payer-family/types';
import { useGetDocDocumentQuery } from '../docDocumentApi';
import { useParams } from 'react-router-dom';

interface DocDocumentLocationsPropTypes {
  locations: DocDocumentLocation[];
}

export const DocDocumentLocations = ({ locations }: DocDocumentLocationsPropTypes) => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  const form = Form.useFormInstance();
  const [editDrawerOpen, setEditDrawerOpen] = useState<boolean>(false);
  const [createDrawerOpen, setCreateDrawerOpen] = useState<boolean>(false);
  const [selectedIndex, setSelectedLocationIndex] = useState<number>(-1);

  const [currentOptions, setCurrentOptions] = useState<
    ({ value: string; label: string } | undefined)[]
  >(
    doc?.locations.map((location) =>
      location.payer_family
        ? {
            value: location.payer_family._id,
            label: location.payer_family.name,
          }
        : undefined
    ) ?? []
  );

  const updatedLocations = Form.useWatch('locations');

  return (
    <div>
      {locations.map((location, index) => (
        <DocDocumentLocationForm
          key={location.site_id}
          index={index}
          location={location}
          onShowPayerFamilyCreate={() => {
            setSelectedLocationIndex(index);
            setCreateDrawerOpen(true);
          }}
          onShowPayerFamilyEdit={() => {
            setSelectedLocationIndex(index);
            setEditDrawerOpen(true);
          }}
          currentOption={currentOptions[index]}
          setCurrentOption={(newCurrentOption?: { value: string; label: string }) => {
            const newCurrentOptions = currentOptions.map((currentOption, i) =>
              index === i ? newCurrentOption : currentOption
            );
            setCurrentOptions(newCurrentOptions);
          }}
        />
      ))}
      {createDrawerOpen ? (
        <PayerFamilyCreateDrawer
          location={locations[selectedIndex]}
          open={createDrawerOpen}
          onSave={(newPayerFamily: PayerFamily) => {
            const newCurrentOptions = currentOptions.map((option, index) =>
              index === selectedIndex
                ? { label: newPayerFamily.name, value: newPayerFamily._id } // update label
                : option
            );
            setCurrentOptions(newCurrentOptions);
            form.setFieldValue(['locations', selectedIndex, 'payer_family_id'], newPayerFamily._id);
            setCreateDrawerOpen(false);
            setSelectedLocationIndex(-1);
          }}
          onClose={() => {
            setCreateDrawerOpen(false);
            setSelectedLocationIndex(-1);
          }}
          mask={false}
        />
      ) : null}

      {editDrawerOpen ? (
        <PayerFamilyEditDrawer
          mask={false}
          location={locations[selectedIndex]}
          payer_family_id={updatedLocations[selectedIndex].payer_family_id}
          open={editDrawerOpen}
          onSave={(updatedPayerFamily: PayerFamily) => {
            const newCurrentOptions = currentOptions.map((option, index) =>
              index === selectedIndex
                ? { label: updatedPayerFamily.name, value: updatedPayerFamily._id } // update label
                : option
            );
            setCurrentOptions(newCurrentOptions);
            setEditDrawerOpen(false);
            setSelectedLocationIndex(-1);
          }}
          onClose={() => {
            setEditDrawerOpen(false);
            setSelectedLocationIndex(-1);
          }}
        />
      ) : null}
    </div>
  );
};
