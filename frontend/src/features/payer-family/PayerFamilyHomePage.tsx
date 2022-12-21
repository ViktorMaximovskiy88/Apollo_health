import { Button } from 'antd';
import { useState } from 'react';
import { MainLayout } from '../../components';
import { PayerFamilyCreateDrawer } from './LocationPayerFamilyCreateDrawer';
import { PayerFamilyEditDrawer } from './LocationPayerFamilyEditDrawer';
import { PayerFamilyTable } from './PayerFamilyDataTable';

export function PayerFamilyHomePage() {
  const [open, setOpen] = useState(false);
  const [openEditDrawer, setOpenEditDrawer] = useState(false);
  const [payerFamilyId, setPayerFamilyId] = useState('');
  return (
    <MainLayout sectionToolbar={<Button onClick={() => setOpen(true)}>Create</Button>}>
      <PayerFamilyTable setOpenEditDrawer={setOpenEditDrawer} setPayerFamilyId={setPayerFamilyId} />

      <PayerFamilyEditDrawer
        mask={true}
        editPayerFromTable={true}
        open={openEditDrawer}
        payer_family_id={payerFamilyId}
        onSave={() => {
          setOpenEditDrawer(false);
        }}
        onClose={() => {
          setOpenEditDrawer(false);
        }}
      />

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
