import { useState } from 'react';
import { Button } from 'antd';
import { useParams } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import {
  useRunSiteScrapeTaskMutation,
  useCancelAllSiteScrapeTasksMutation,
} from './siteScrapeTasksApi';
import { useGetSiteQuery } from '../sites/sitesApi';
import { CollectionsDataTable } from './CollectionsDataTable';
import { CollectionMethod } from '../sites/types';
import { ErrorLogModal } from './ErrorLogModal';
import { SiteStatus } from '../sites/siteStatus';
import { SiteMenu } from '../sites/SiteMenu';
import { TaskStatus } from '../../common/scrapeTaskStatus';
import { MainLayout } from '../../components';

export function CollectionsPage() {
  const [modalVisible, setModalVisible] = useState(false);
  const [errorTraceback, setErrorTraceback] = useState('');

  const openErrorModal = (errorTraceback: string): void => {
    setErrorTraceback(errorTraceback);
    setModalVisible(true);
  };

  const params = useParams();
  const siteId = params.siteId;
  const { data: site, refetch } = useGetSiteQuery(siteId);
  const [runScrape] = useRunSiteScrapeTaskMutation();
  if (!siteId) return null;
  return (
    <>
      <ErrorLogModal
        visible={modalVisible}
        setVisible={setModalVisible}
        errorTraceback={errorTraceback}
      />
      <MainLayout
        sidebar={<SiteMenu />}
        pageTitle={'Collections'}
        pageToolbar={
          <>
            {site &&
            site.collection_method === CollectionMethod.Automated &&
            site.status !== SiteStatus.Inactive ? (
              <Button onClick={() => runScrape(site._id)} className="ml-auto">
                Run Collection
              </Button>
            ) : site &&
              site.collection_method === CollectionMethod.Manual &&
              site.status !== SiteStatus.Inactive ? (
              <ManualCollectionButton site={site} refetch={refetch} runScrape={runScrape} />
            ) : null}
          </>
        }
      >
        <CollectionsDataTable siteId={siteId} openErrorModal={openErrorModal} />
      </MainLayout>
    </>
  );
}

function ManualCollectionButton(props: any) {
  const { site, refetch, runScrape } = props;
  const navigate = useNavigate();
  const [cancelAllScrapes] = useCancelAllSiteScrapeTasksMutation();

  async function handleRunScrape() {
    let response: any = await runScrape(site!._id);
    if (response) {
      refetch();
      navigate(`../documents?scrape_task_id=${response.data._id}`);
    }
  }
  async function handleCancelScrape() {
    await cancelAllScrapes(site!._id);
    refetch();
  }
  const activeStatuses = [TaskStatus.Queued, TaskStatus.Pending, TaskStatus.InProgress];
  if (activeStatuses.includes(site.last_run_status)) {
    return (
      <Button className="ml-auto" onClick={handleCancelScrape}>
        End Manual Collection
      </Button>
    );
  } else {
    return (
      <Button className="ml-auto" onClick={handleRunScrape}>
        Start Manual Collection
      </Button>
    );
  }
}
