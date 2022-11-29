import { Button } from 'antd';
import { useState } from 'react';
import { MainLayout } from '../../components';
import { PayerFamilyCreateDrawer } from './LocationPayerFamilyCreateDrawer';
import { PayerFamilyTable } from './PayerFamilyDataTable';

export function PayerFamilyHomePage() {
  const [open, setOpen] = useState(false);
  return (
    <MainLayout sectionToolbar={<Button onClick={() => setOpen(true)}>Create</Button>}>
      <PayerFamilyTable />
      <PayerFamilyCreateDrawer
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
