import { useParams } from 'react-router-dom';
import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';
import { ExtractionResultsDataTable } from './ExtractionResultsDataTable';

export function ExtractionEditPage() {
  const { extractionId } = useParams();

  return (
    <MainLayout sidebar={<SiteMenu />} pageTitle="Extraction Results">
      <ExtractionResultsDataTable extractionId={extractionId} />
    </MainLayout>
  );
}
