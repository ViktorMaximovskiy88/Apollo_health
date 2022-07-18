import { Layout } from 'antd';
import Title from 'antd/lib/typography/Title';
import { DocDocumentsDataTable } from './DocDocumentsDataTable';
import { PageHeader, PageLayout } from '../../components';

export function DocDocumentsHomePage() {
  return (
    <PageLayout>
      <PageHeader header={'Documents'} />

      <DocDocumentsDataTable />
    </PageLayout>
  );
}
