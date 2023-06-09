import { AppBreadcrumbs } from '../app/AppLayout';
import { Layout } from './Layout';

interface PropTypes {
  title?: any;
  children?: any;
  breadcrumbs?: boolean;
  sectionToolbar?: any;
  sidebar?: any;
}

export function MainLayout({ sectionToolbar, sidebar, breadcrumbs = true, children }: PropTypes) {
  const useSection = !!(sectionToolbar || sidebar || breadcrumbs);

  return useSection ? (
    <Layout
      title={<AppBreadcrumbs />}
      sidebar={sidebar}
      toolbar={sectionToolbar}
      gap={false}
      border={true}
    >
      <Layout>{children}</Layout>
    </Layout>
  ) : (
    <Layout>{children}</Layout>
  );
}

export function DevToolsLayout({ title, sectionToolbar, sidebar, children }: PropTypes) {
  return (
    <Layout title={title} sidebar={sidebar} gap={false} border={true} toolbar={sectionToolbar}>
      <Layout>{children}</Layout>
    </Layout>
  );
}
