import { Button } from 'antd';
import { useState } from 'react';
import { MainLayout } from '../../../components';
import { DocumentFamilyCreateDrawer } from './DocumentFamilyCreateDrawer';
import { DocumentFamilyTable } from './DocumentFamilyDataTable';

export function DocumentFamilyHomePage() {
  const [open, setOpen] = useState(false);
  return (
    <MainLayout sectionToolbar={<Button onClick={() => setOpen(true)}>Create</Button>}>
      <DocumentFamilyTable />
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
