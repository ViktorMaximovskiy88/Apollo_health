import { Layout, Menu } from 'antd';
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
import { DocDocumentsHomePage } from './features/doc_documents/DocDocumentsHomePage';
import { DocumentEditPage } from './features/retrieved_documents/DocumentEditPage';
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
import { ItemType } from 'antd/lib/menu/hooks/useItems';
import tw from 'twin.macro';
import { DocDocumentEditPage } from './features/doc_documents/DocDocumentEditPage';

function TopNav() {
  const location = useLocation();
  const params = useParams();
  const { user, logout } = useAuth0();
  const siteId = params.siteId;
  const { data: site } = useGetSiteQuery(siteId, { skip: !siteId });
  const current = location.pathname.split('/')[1];
  const sections = [
    { key: 'sites', label: 'Sites' },
    { key: 'documents', label: 'Documents' },
    { key: 'users', label: 'Users' },
  ];
  const siteLabel = <>
      {site?._id === params.siteId && (
        <Link
          style={{ marginTop: -1, ...tw`text-blue-500` }}
          to={`/sites/${params.siteId}/scrapes`}
        >
          {site?.name}
        </Link>
      )}
  </>
  const items: ItemType[] = [
    { key: 'site', label: <Link to="/sites">Source Hub</Link>, },
    { key: 'header', label: siteLabel, className: "flex mr-auto" },
  ]
  sections.forEach(({ key, label }) => (
    items.push({ key, label: <Link to={`/${key}`}>{label}</Link> })
  ))
  items.push({
    key: 'profile',
    label: `${user?.given_name} ${user?.family_name}`,
    children: [
      { key: 'logout', label: 'Logout', onClick: () => logout({ returnTo: window.location.origin }) }
    ]
  });
  return (
    <Layout className="h-screen">
      <Layout.Header className="p-0 h-10 bg-white leading-10">
        <Menu
          mode="horizontal"
          selectedKeys={[current]}
          className="justify-end items-center"
          items={items}
        />
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

function DocumentRoutes() {
  return (
    <Routes>
      <Route index element={<DocDocumentsHomePage />} />
      <Route path=":docDocumentId" element={<DocDocumentEditPage />} />
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
        <Route path="/documents/*" element={<DocumentRoutes />} />
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
