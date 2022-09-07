import { useState } from 'react';
import { Button, notification } from 'antd';
import { useParams } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import {
  useRunSiteScrapeTaskMutation,
  useCancelAllSiteScrapeTasksMutation,
} from './siteScrapeTasksApi';
import { useGetSiteQuery } from '../sites/sitesApi';
import { CollectionsDataTable } from './CollectionsDataTable';
import { CollectionMethod } from '../sites/types';
import { AddDocumentModal } from './addDocumentModal';
import { SiteStatus } from '../sites/siteStatus';
import { SiteMenu } from '../sites/SiteMenu';
import { TaskStatus } from '../../common/scrapeTaskStatus';
import { MainLayout } from '../../components';
import { isErrorWithData } from '../../common/helpers';

export function CollectionsPage() {
  const [newDocumentModalVisible, setNewDocumentModalVisible] = useState(false);

  const params = useParams();
  const siteId = params.siteId;
  const { data: site, refetch } = useGetSiteQuery(siteId);
  const [runScrape] = useRunSiteScrapeTaskMutation();

  if (!siteId || !site) return null;

  async function handleRunScrape() {
    if (site?._id) {
      try {
        await runScrape(site._id).unwrap();
        refetch();
      } catch (err) {
        if (isErrorWithData(err)) {
          notification.error({
            message: 'Error Running Collection',
            description: `${err.data.detail}`,
          });
        } else {
          notification.error({
            message: 'Error Running Collection',
            description: JSON.stringify(err),
          });
        }
      }
    }
  }

  return (
    <>
      {newDocumentModalVisible ? (
        <AddDocumentModal setVisible={setNewDocumentModalVisible} siteId={siteId} />
      ) : null}
      <MainLayout
        sidebar={<SiteMenu />}
        pageTitle={'Collections'}
        pageToolbar={
          <>
            {site.collection_method === CollectionMethod.Automated &&
            site.status !== SiteStatus.Inactive ? (
              <Button onClick={() => handleRunScrape()} className="ml-auto">
                Run Collection
              </Button>
            ) : site.collection_method === CollectionMethod.Manual &&
              site.status !== SiteStatus.Inactive ? (
              <ManualCollectionButton site={site} refetch={refetch} runScrape={runScrape} />
            ) : null}
          </>
        }
      >
        <CollectionsDataTable
          siteId={siteId}
          openNewDocumentModal={() => setNewDocumentModalVisible(true)}
        />
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
      navigate(`../doc-documents?scrape_task_id=${response.data._id}`);
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
