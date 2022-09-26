import { Button } from 'antd';
import { Link } from 'react-router-dom';
import { MainLayout } from '../../components';
import { PayerBackboneDataTable } from './PayerBackboneDataTable';
import { PayerBackboneSubMenu } from './PayerBackboneSubMenu';

export function PayerBackbomeHomePage() {
  return (
    <MainLayout
      sidebar={<PayerBackboneSubMenu />}
      sectionToolbar={
        <Link className="ml-auto" to="new">
          <Button>Create</Button>
        </Link>
      }
    >
      <PayerBackboneDataTable />
    </MainLayout>
  );
}
