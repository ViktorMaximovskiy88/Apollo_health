import classNames from 'classnames';
import { PageLayout } from './PageLayout';
import { SectionLayout } from './SectionLayout';

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

  return (
    <div className={classNames('flex flex-col flex-1')}>
      {useSection ? (
        <SectionLayout sidebar={sidebar} toolbar={sectionToolbar}>
          <PageLayout toolbar={pageToolbar} title={pageTitle} section={true}>
            {children}
          </PageLayout>
        </SectionLayout>
      ) : (
        <PageLayout toolbar={pageToolbar} title={pageTitle}>
          {children}
        </PageLayout>
      )}
    </div>
  );
}
