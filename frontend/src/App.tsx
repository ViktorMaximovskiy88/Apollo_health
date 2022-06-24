import { Layout, Menu, Avatar } from 'antd';
import {
  Link,
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
  useParams,
} from 'react-router-dom';

import { withAuthenticationRequired, User } from '@auth0/auth0-react';
import { DocumentsHomePage } from './features/documents/DocumentsHomePage';
import { DocumentEditPage } from './features/documents/DocumentEditPage';
import { CollectionsPage } from './features/collections/CollectionsPage';
import { SiteCreatePage } from './features/sites/SiteCreatePage';
import { SiteEditPage } from './features/sites/SiteEditPage';
import { SitePage } from './features/sites/SitePage';
import { useGetSiteQuery } from './features/sites/sitesApi';
import { SitesHomePage } from './features/sites/SitesHomePage';
import { UserCreatePage } from './features/users/UserCreatePage';
import { UserEditPage } from './features/users/UserEditPage';
import { UsersHomePage } from './features/users/UserHomePage';
import { DocumentsPage } from './features/sites/DocumentsPage';
import { ExtractionsPage } from './features/extractions/ExtractionsPage';
import { DocExtractionPage } from './features/extractions/DocExtractionPage';
import { ExtractionEditPage } from './features/extractions/ExtractionEditPage';
import { useAuth0 } from '@auth0/auth0-react';

function TopNav() {
  const location = useLocation();
  const params = useParams();
  const { user, logout } = useAuth0();
  const siteId = params.siteId;
  const { data: site } = useGetSiteQuery(siteId, { skip: !siteId });
  const current = location.pathname.split('/')[1];
  const sections = [
    { key: 'sites', label: 'Sites' },
    { key: 'users', label: 'Users' },
  ];
  return (
    <Layout className="h-screen">
      <Layout.Header className="p-0 h-10 bg-white leading-10">
        <Menu
          mode="horizontal"
          selectedKeys={[current]}
          className="justify-end items-center"
        >
          <div className="flex mr-auto">
            <Menu.Item key={'sites'}>
              <Link to={`/sites`}>Source Hub</Link>
            </Menu.Item>
            {site?._id === params.siteId && (
              <Link
                style={{ marginTop: -1 }}
                to={`/sites/${params.siteId}/scrapes`}
              >
                {site?.name}
              </Link>
            )}
          </div>
          {sections.map(({ key, label }) => (
            <Menu.Item key={key}>
              <Link to={`/${key}`}>{label}</Link>
            </Menu.Item>
          ))}
          <Menu.Item key={'profile'}>
            <Menu.SubMenu title={`${user?.given_name} ${user?.family_name}`}>
              <Menu.Item
                onClick={() => {
                  logout();
                }}
              >
                Logout
              </Menu.Item>
            </Menu.SubMenu>
          </Menu.Item>
        </Menu>
      </Layout.Header>
      <Layout className="bg-white overflow-auto">
        <Outlet />
      </Layout>
    </Layout>
  );
}

function AppHomePage() {
  return <>{'Home'}</>;
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

function App() {
  return (
    <Routes>
      <Route path="/" element={<TopNav />}>
        <Route path="/home/*" element={<AppHomePage />} />
        <Route path="/sites">
          <Route index element={<SitesHomePage />} />
          <Route path="new" element={<SiteCreatePage />} />
          <Route path=":siteId">
            <Route path="edit" element={<SiteEditPage />} />
            <Route element={<SitePage />}>
              <Route path="scrapes" element={<CollectionsPage />} />
              <Route path="documents">
                <Route index element={<DocumentsPage />} />
                <Route path=":docId">
                  <Route path="edit" element={<DocumentEditPage />} />
                </Route>
              </Route>
              <Route path="extraction">
                <Route index element={<ExtractionsPage />} />
                <Route path="document/:docId">
                  <Route index element={<DocExtractionPage />} />
                  <Route
                    path=":extractionId"
                    element={<ExtractionEditPage />}
                  />
                </Route>
              </Route>
            </Route>
          </Route>
        </Route>
        <Route path="/users/*" element={<UserRoutes />} />
        <Route path="/" element={<Navigate replace to="/sites" />} />
      </Route>
    </Routes>
  );
}

export default withAuthenticationRequired(App, {
  loginOptions: { redirectTo: '/sites' },
  claimCheck: function (user?: User): boolean {
    return true;
  },
});
