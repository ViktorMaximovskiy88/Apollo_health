import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Button } from 'antd';
import { MainLayout } from '../../components';
import { DocumentsTable } from './DocumentsTable';
import { AddDocumentModal } from "../collections/addDocumentModal";
import { useGetSiteQuery } from './sitesApi';
import { SiteMenu } from './SiteMenu';
import { CollectionMethod } from "./types";

export function DocumentsPage() {
  const params = useParams();
  const [newDocumentModalVisible, setNewDocumentModalVisible] = useState(false);
  const { data: site } = useGetSiteQuery(params.siteId);
  return (
    <MainLayout
      sidebar={<SiteMenu />}
      pageTitle={'Documents'}
      pageToolbar={
        site && site.collection_method == CollectionMethod.Manual ?
        <Button onClick={() => setNewDocumentModalVisible(true)} className="ml-auto">Create Document</Button>
        :
        null
      }
    >
      <DocumentsTable />
      {
        newDocumentModalVisible ?
        <AddDocumentModal
          setVisible={setNewDocumentModalVisible}
          siteId={params.siteId}
        />
        :
        null
      }
    </MainLayout>
  );
}
