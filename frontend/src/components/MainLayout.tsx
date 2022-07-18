import classNames from 'classnames';
import { PageLayout } from './PageLayout';
import { SectionLayout } from './SectionLayout';

interface PropTypes {
  children?: any;
  pageTitle?: any;
  pageToolbar?: any;
  sectionTitle?: any;
  sectionToolbar?: any;
  sidebar?: any;
}

export function MainLayout({
  pageTitle,
  pageToolbar,
  sectionToolbar,
  sidebar,
  children,
}: PropTypes) {
  const useSection = !!(sectionToolbar || sidebar);
  return (
    <div className={classNames('')}>
      {useSection ? (
        <SectionLayout sidebar={sidebar} toolbar={sectionToolbar}>
          <PageLayout toolbar={pageToolbar} title={pageTitle}>
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
