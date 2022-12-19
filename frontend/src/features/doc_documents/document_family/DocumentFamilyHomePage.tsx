import { Button } from 'antd';
import { useState } from 'react';
import { MainLayout } from '../../../components';
import { DocumentFamilyCreateDrawer } from './DocumentFamilyCreateDrawer';
import { DocumentFamilyTable } from './DocumentFamilyDataTable';
import { DocumentFamilyEditDrawer } from './DocumentFamilyEditDrawer';

export function DocumentFamilyHomePage() {
  const [open, setOpen] = useState(false);
  const [openEditDrawer, setOpenEditDrawer] = useState(false);
  const [docFamilyId, setDocFamilyId] = useState('');

  return (
    <MainLayout sectionToolbar={<Button onClick={() => setOpen(true)}>Create</Button>}>
      <DocumentFamilyTable setDocFamilyId={setDocFamilyId} setOpenEditDrawer={setOpenEditDrawer} />
      <DocumentFamilyEditDrawer
        mask={true}
        docFamilyId={docFamilyId}
        open={openEditDrawer}
        onSave={() => {
          setOpenEditDrawer(false);
        }}
        onClose={() => {
          setOpenEditDrawer(false);
        }}
      />
      <DocumentFamilyCreateDrawer
        open={open}
        onSave={() => {
          setOpen(false);
        }}
        onClose={() => {
          setOpen(false);
        }}
      />
    </MainLayout>
  );
}
