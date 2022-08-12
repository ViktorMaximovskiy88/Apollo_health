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
import { ErrorLogModal } from './ErrorLogModal';
import { AddDocumentModal } from './addDocumentModal';
import { SiteStatus } from '../sites/siteStatus';
import { SiteMenu } from '../sites/SiteMenu';
import { TaskStatus } from '../../common/scrapeTaskStatus';
import { MainLayout } from '../../components';
import { isErrorWithData } from '../../common/helpers';

export function CollectionsPage() {
  const [modalVisible, setModalVisible] = useState(false);
  const [errorTraceback, setErrorTraceback] = useState('');
  const [newDocumentModalVisible, setNewDocumentModalVisible] = useState(false);
  const openErrorModal = (errorTraceback: string): void => {
    setErrorTraceback(errorTraceback);
    setModalVisible(true);
  };

  const params = useParams();
  const siteId = params.siteId;
  const { data: site, refetch } = useGetSiteQuery(siteId);
  const [runScrape] = useRunSiteScrapeTaskMutation();
  if (!siteId) return null;

  async function handleRunScrape() {
    if (site?._id) {
      try {
        await runScrape(site._id).unwrap();
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
      <ErrorLogModal
        visible={modalVisible}
        setVisible={setModalVisible}
        errorTraceback={errorTraceback}
      />
      {newDocumentModalVisible ? (
        <AddDocumentModal setVisible={setNewDocumentModalVisible} siteId={siteId} />
      ) : null}
      <MainLayout
        sidebar={<SiteMenu />}
        pageTitle={'Collections'}
        pageToolbar={
          <>
            {site &&
            site.collection_method === CollectionMethod.Automated &&
            site.status !== SiteStatus.Inactive ? (
              <Button onClick={() => handleRunScrape()} className="ml-auto">
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
        <CollectionsDataTable
          siteId={siteId}
          openErrorModal={openErrorModal}
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
