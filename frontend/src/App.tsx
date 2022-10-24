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
import { SiteDocDocumentsPage } from './features/doc_documents/SiteDocDocumentPage';
import { DocDocumentEditPage } from './features/doc_documents/DocDocumentEditPage';
import { PayerFamilyHomePage } from './features/payer-family/PayerFamilyHomePage';
import { PayerFamilyEditPage } from './features/payer-family/PayerFamilyEditPage';
import { ProcessWorkItemPage, ReadonlyWorkItemPage } from './features/work_queue/WorkItemPage';
import { AppLayout } from './app/AppLayout';
import { SiteViewPage } from './features/sites/SiteViewPage';
import { TranslationsHomePage } from './features/translations/TranslationsHomePage';
import { TranslationsNewPage } from './features/translations/TranslationsNewPage';
import { TranslationsEditPage } from './features/translations/TranslationsEditPage';
import { PayerBackbomeHomePage } from './features/payer-backbone/PayerBackboneHomePage';
import { PayerBackboneNewPage } from './features/payer-backbone/PayerBackboneNewPage';
import { PayerBackboneEditPage } from './features/payer-backbone/PayerBackboneEditPage';
import { LineagePage } from './features/lineage/LineagePage';
import { StatsRoutes } from './features/stats';
import { DocumentFamilyHomePage } from './features/doc_documents/document_family/DocumentFamilyHomePage';
import { DocumentFamilyEditPage } from './features/doc_documents/document_family/documentFamilyEditPage';

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
function DocumentFamilyRoutes() {
  return (
    <Routes>
      <Route index element={<DocumentFamilyHomePage />} />
      <Route path=":documentFamilyId" element={<DocumentFamilyEditPage />} />
    </Routes>
  );
}

function TranslationRoutes() {
  return (
    <Routes>
      <Route index element={<TranslationsHomePage />} />
      <Route path="/new" element={<TranslationsNewPage />} />
      <Route path=":translationId" element={<TranslationsEditPage />} />
    </Routes>
  );
}

function PayerBackboneRoutes() {
  return (
    <Routes>
      <Route path=":payerType" element={<PayerBackbomeHomePage />} />
      <Route path=":payerType/new" element={<PayerBackboneNewPage />} />
      <Route path=":payerType/:payerId" element={<PayerBackboneEditPage />} />
      <Route path="/" element={<Navigate replace to="./plan" />} />
    </Routes>
  );
}

function PayerFamilyRoutes() {
  return (
    <Routes>
      <Route index element={<PayerFamilyHomePage />} />
      <Route path=":payerFamilyId" element={<PayerFamilyEditPage />} />
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
            <Route path=":docDocumentId">
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
            <Route index element={<Navigate to="edit" replace={true} />} />
            <Route path="view" element={<SiteViewPage />} />
            <Route path="edit" element={<SiteEditPage />} />
            <Route path="scrapes" element={<CollectionsPage />} />
            <Route path="documents">
              <Route index element={<SiteRetreivedDocumentsPage />} />
              <Route path=":docId">
                <Route path="edit" element={<DocumentEditPage />} />
              </Route>
            </Route>
            <Route path="lineage" element={<LineagePage />} />
            <Route path="extraction">
              <Route index element={<ExtractionsPage />} />
              <Route path="document/:docId">
                <Route index element={<DocExtractionPage />} />
                <Route path=":extractionId/results" element={<ExtractionEditPage />} />
              </Route>
            </Route>
            <Route path="doc-documents">
              <Route index element={<SiteDocDocumentsPage />} />
              <Route path=":docId">
                <Route path="edit" element={<DocDocumentEditPage />} />
              </Route>
            </Route>
          </Route>
        </Route>
        <Route path="/payer-family" element={<PayerFamilyHomePage />} />
        <Route path="/document-family/*" element={<DocumentFamilyRoutes />} />
        <Route path="/payer-family/*" element={<PayerFamilyRoutes />} />
        <Route path="/users/*" element={<UserRoutes />} />
        <Route path="/documents/*" element={<DocumentRoutes />} />
        <Route path="/translations/*" element={<TranslationRoutes />} />
        <Route path="/payer-backbone/*" element={<PayerBackboneRoutes />} />
        <Route path="/stats/*" element={<StatsRoutes />} />
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
