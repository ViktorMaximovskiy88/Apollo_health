import { Layout, Menu } from 'antd';
import {
  Link,
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom';
import { DocumentsHomePage } from './features/documents/DcoumentsHomePage';
import { DocumentEditPage } from './features/documents/DocumentEditPage';
import { SiteCreatePage } from './features/sites/SiteCreatePage';
import { SiteEditPage } from './features/sites/SiteEditPage';
import { SitePage } from './features/sites/SitePage';
import { SitesHomePage } from './features/sites/SitesHomePage';
import { UserCreatePage } from './features/users/UserCreatePage';
import { UserEditPage } from './features/users/UserEditPage';
import { UsersHomePage } from './features/users/UserHomePage';

function TopNav() {
  const location = useLocation();
  const current = location.pathname.split('/')[1];
  const sections = [
    { key: 'home', label: 'Dashboard' },
    { key: 'sites', label: 'Sites' },
    { key: 'documents', label: 'Documents' },
    { key: 'users', label: 'Users' },
  ];
  return (
    <Layout className="h-screen">
      <Layout.Header className="p-0 h-10 leading-10">
        <Menu mode="horizontal" selectedKeys={[current]}>
          {sections.map(({ key, label }) => (
            <Menu.Item key={key}>
              <Link to={`/${key}`}>{label}</Link>
            </Menu.Item>
          ))}
        </Menu>
      </Layout.Header>
      <Layout className="p-4 bg-white overflow-auto">
        <Outlet />
      </Layout>
    </Layout>
  );
}

function AppHomePage() {
  return <>{'Home'}</>;
}

function SiteRoutes() {
  return (
    <Routes>
      <Route index element={<SitesHomePage />} />
      <Route path="new" element={<SiteCreatePage />} />
      <Route path=":siteId">
        <Route index element={<SitePage />} />
        <Route path="edit" element={<SiteEditPage />} />
      </Route>
    </Routes>
  );
}

function UserRoutes() {
  return (
    <Routes>
      <Route index element={<UsersHomePage />} />
      <Route path="new" element={<UserCreatePage />} />
      <Route path=":userId">
        <Route path="edit" element={<UserEditPage />} />
      </Route>
    </Routes>
  );
}
function DocumentRoutes() {
  return (
    <Routes>
      <Route index element={<DocumentsHomePage />} />
      <Route path=":docId" >
        <Route path="edit" element={<DocumentEditPage/>}/>
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<TopNav />}>
        <Route path="/home/*" element={<AppHomePage />} />
        <Route path="/sites/*" element={<SiteRoutes />} />
        <Route path="/documents/*" element={<DocumentRoutes />} />
        <Route path="/users/*" element={<UserRoutes />} />
        <Route path="/" element={<Navigate replace to="/home" />} />
      </Route>
    </Routes>
  );
}

export default App;
