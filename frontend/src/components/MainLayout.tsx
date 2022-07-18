import { AppBreadcrumbs } from '../app/AppLayout';
import { Layout } from './Layout';

interface PropTypes {
  children?: any;
  pageTitle?: any;
  pageToolbar?: any;
  breadcrumbs?: boolean;
  sectionToolbar?: any;
  sidebar?: any;
}

export function MainLayout({
  pageTitle,
  pageToolbar,
  sectionToolbar,
  sidebar,
  breadcrumbs = true,
  children,
}: PropTypes) {
  const useSection = !!(sectionToolbar || sidebar || breadcrumbs);

  return useSection ? (
    <Layout title={<AppBreadcrumbs />} sidebar={sidebar} toolbar={sectionToolbar} gap={false}>
      <Layout toolbar={pageToolbar} title={pageTitle}>
        {children}
      </Layout>
    </Layout>
  ) : (
    <Layout toolbar={pageToolbar} title={pageTitle}>
      {children}
    </Layout>
  );
}
