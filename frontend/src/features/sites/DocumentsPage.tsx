import { useState } from "react";
import { useParams } from "react-router-dom";
import { Button } from 'antd';
import Title from 'antd/lib/typography/Title';
import { DocumentsTable } from './DocumentsTable';
import { AddDocumentModal } from "../collections/addDocumentModal";


export function DocumentsPage() {
  const params = useParams();
  const [newDocumentModalVisible, setNewDocumentModalVisible]= useState(false);
  return (
    <>
      <div className="flex">
        <Title className="inline-block" level={4}>
          Documents
        </Title>
        <Button onClick={() => setNewDocumentModalVisible(true)} className="ml-auto">Create Document</Button>
      </div>
      <AddDocumentModal
        visible={newDocumentModalVisible}
        setVisible={setNewDocumentModalVisible}
        siteId={params.siteId}
      />
      <DocumentsTable />
    </>
  );
}
