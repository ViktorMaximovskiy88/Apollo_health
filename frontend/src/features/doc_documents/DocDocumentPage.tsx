import { DocDocumentsDataTable } from './DocDocumentsDataTable';
import { MainLayout } from '../../components';
import { Button } from 'antd';
import { SiteMenu } from '../sites/SiteMenu';
import { DocDocumentsTable } from "./DocDocumentsTable";

export function DocDocumentsPage() {
  return (
    <MainLayout 
      pageTitle={'Doc Documents'}
      sidebar={<SiteMenu />}
      pageToolbar={
        <>
          <Button className="ml-auto">Create Document</Button>
        </>
      }
      >
      <DocDocumentsTable />
    </MainLayout>
  );
}
