import { Button } from 'antd';
import { Link } from 'react-router-dom';
import { MainLayout } from '../../components';
import { TranslationsDataTable } from './TranslationsDataTable';

export function TranslationsHomePage() {
  return (
    <MainLayout
      sectionToolbar={
        <Link className="ml-auto" to="new">
          <Button>Create</Button>
        </Link>
      }
    >
      <TranslationsDataTable />
    </MainLayout>
  );
}
