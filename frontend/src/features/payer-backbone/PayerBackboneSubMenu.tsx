import { Layout, Menu } from 'antd';
import { Link, useParams } from 'react-router-dom';

export function PayerBackboneSubMenu() {
  const { payerType } = useParams();

  const subpages = [
    { key: 'plan', label: <Link to={`/payer-backbone/plan`}>Plan</Link> },
    { key: 'formulary', label: <Link to={`/payer-backbone/formulary`}>Formulary</Link> },
    { key: 'ump', label: <Link to={`/payer-backbone/ump`}>UM Package</Link> },
    { key: 'bm', label: <Link to={`/payer-backbone/bm`}>Benefit Manager</Link> },
    { key: 'mco', label: <Link to={`/payer-backbone/mco`}>MCO</Link> },
    { key: 'parent', label: <Link to={`/payer-backbone/parent`}>Parent</Link> },
  ];

  return (
    <Layout.Sider width={175}>
      <Menu mode="inline" className="h-full" selectedKeys={[payerType ?? '']} items={subpages} />
    </Layout.Sider>
  );
}
