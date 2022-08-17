import { Navigate, Route, Routes } from 'react-router-dom';
import { withAuthenticationRequired, User } from '@auth0/auth0-react';

import { DocDocumentsHomePage } from './features/doc_documents/DocDocumentsHomePage';
import { DocumentEditPage } from './features/retrieved_documents/DocumentEditPage';
import { CollectionsPage } from './features/collections/CollectionsPage';
import { SiteCreatePage } from './features/sites/SiteCreatePage';
import { SiteEditPage } from './features/sites/SiteEditPage';
import { SitesHomePage } from './features/sites/SitesHomePage';
import { UserCreatePage } from './features/users/UserCreatePage';
import { UserEditPage } from './features/users/UserEditPage';
import { UsersHomePage } from './features/users/UserHomePage';
import { SiteRetreivedDocumentsPage } from './features/sites/SiteRetreivedDocumentsPage';
import { ExtractionsPage } from './features/extractions/ExtractionsPage';
import { DocExtractionPage } from './features/extractions/DocExtractionPage';
import { ExtractionEditPage } from './features/extractions/ExtractionEditPage';
import { WorkQueueHomePage } from './features/work_queue/WorkQueueHomePage';
import { WorkQueuePage } from './features/work_queue/WorkQueuePage';
import { DocDocumentsPage } from './features/doc_documents/DocDocumentPage';
import { DocDocumentEditPage } from './features/doc_documents/DocDocumentEditPage';
import { ProcessWorkItemPage, ReadonlyWorkItemPage } from './features/work_queue/WorkItemPage';
import { AppLayout } from './app/AppLayout';
import { SiteViewPage } from './features/sites/SiteViewPage';

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
      <Route path="/" element={<AppLayout />}>
        <Route path="/home/*" element={<AppHomePage />} />
        <Route path="/work-queues">
          <Route index element={<WorkQueueHomePage />} />
          <Route path=":queueId">
            <Route index element={<WorkQueuePage />} />
            <Route path=":itemId">
              <Route path="process" element={<ProcessWorkItemPage />} />
              <Route path="read-only" element={<ReadonlyWorkItemPage />} />
            </Route>
          </Route>
        </Route>
        <Route path="/sites">
          <Route index element={<SitesHomePage />} />
          <Route path="new" element={<SiteCreatePage />} />
          <Route path=":siteId">
            {/* duped because we want this */}
            <Route index element={<Navigate to="edit" />} />
            <Route path="view" element={<SiteViewPage />} />
            <Route path="edit" element={<SiteEditPage />} />
            <Route path="scrapes" element={<CollectionsPage />} />
            <Route path="documents">
              <Route index element={<SiteRetreivedDocumentsPage />} />
              <Route path=":docId">
                <Route path="edit" element={<DocumentEditPage />} />
              </Route>
            </Route>
            <Route path="extraction">
              <Route index element={<ExtractionsPage />} />
              <Route path="document/:docId">
                <Route index element={<DocExtractionPage />} />
                <Route path=":extractionId" element={<ExtractionEditPage />} />
              </Route>
            </Route>
            <Route path="doc-documents">
              <Route index element={<DocDocumentsPage />} />
              <Route path=":docId">
                <Route path="edit" element={<DocDocumentEditPage />} />
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
