import { useContext, useEffect, useState } from 'react';
import { Button, notification } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import {
  useRunSiteScrapeTaskMutation,
  useCancelAllSiteScrapeTasksMutation,
  useLazyGetScrapeTasksForSiteQuery,
} from './siteScrapeTasksApi';
import { useGetSiteQuery, useLazyGetSiteDocDocumentsQuery } from '../sites/sitesApi';
import { CollectionsDataTable } from './CollectionsDataTable';
import { CollectionMethod } from '../sites/types';
import { AddDocumentModal } from './AddDocumentModal';
import { SiteStatus } from '../sites/siteStatus';
import { SiteMenu } from '../sites/SiteMenu';
import { TaskStatus } from '../../common/scrapeTaskStatus';
import { MainLayout } from '../../components';
import { isErrorWithData } from '../../common/helpers';
import { useSiteScrapeTaskId } from '../doc_documents/manual_collection/useUpdateSelected';
import { initialState } from './collectionsSlice';
import { ValidationButtonsContext } from '../doc_documents/manual_collection/ManualCollectionContext';

function ManualCollectionButton(props: any) {
  const { site, refetch, runScrape } = props;
  const navigate = useNavigate();
  const [cancelAllScrapes] = useCancelAllSiteScrapeTasksMutation();
  const [isLoading, setIsLoading] = useState(false);
  const activeStatuses = [TaskStatus.Queued, TaskStatus.Pending, TaskStatus.InProgress];
  const scrapeTaskId = useSiteScrapeTaskId();
  const [getScrapeTasksForSiteQuery] = useLazyGetScrapeTasksForSiteQuery();
  const [getDocDocumentsQuery] = useLazyGetSiteDocDocumentsQuery();
  const [refreshSiteDocs, setRefreshSiteDocs] = useState(false);

  const mostRecentTask = {
    limit: 1,
    skip: 0,
    sortInfo: initialState.table.sort,
    filterValue: initialState.table.filter,
  };

  const refreshDocs = async () => {
    if (!scrapeTaskId) return;
    if (!site) return;
    const siteId = site._id;
    await getScrapeTasksForSiteQuery({ ...mostRecentTask, siteId });
    await getDocDocumentsQuery({ siteId, scrapeTaskId });
  };

  useEffect(() => {
    if (refreshSiteDocs) {
      refreshDocs();
      setRefreshSiteDocs(false);
    }
  });

  async function handleRunManualScrape() {
    try {
      setIsLoading(true);
      let response: any = await runScrape(site!._id);
      if (response.data.success) {
        refetch();
        setRefreshSiteDocs(true);
        setTimeout(function () {
          setIsLoading(false);
          navigate(`../doc-documents?scrape_task_id=${response.data.nav_id}`);
        }, 500); // refetch sometimes not working. delay and refetch again.
      } else {
        setIsLoading(false);
        notification.error({
          message: 'Error Running Manual Collection',
          description: response.data.errors[0],
        });
      }
    } catch (err) {
      if (isErrorWithData(err)) {
        setIsLoading(false);
        notification.error({
          message: 'Error Running Manual Collection',
          description: `${err.data.detail}`,
        });
      } else {
        setIsLoading(false);
        notification.error({
          message: 'Error Running Manual Collection',
          description: JSON.stringify(err),
        });
      }
    }
  }

  async function handleCancelManualScrape() {
    if (site?._id) {
      try {
        setIsLoading(true);
        let response: any = await cancelAllScrapes(site!._id);
        if (response.data?.success) {
          refetch();
          setRefreshSiteDocs(true);
          setTimeout(function () {
            setIsLoading(false);
          }, 500); // refetch sometimes not working. delay and refetch again.
        } else {
          setIsLoading(false);
          notification.error({
            message: 'Please review and update the following documents',
            description: response.error.data.detail,
          });
        }
      } catch (err) {
        if (isErrorWithData(err)) {
          setIsLoading(false);
          notification.error({
            message: 'Error Cancelling Collection',
            description: `${err.data.detail}`,
          });
        } else {
          setIsLoading(false);
          notification.error({
            message: 'Error Cancelling Collection',
            description: 'Unknown error.',
          });
        }
      }
    }
  }

  if (activeStatuses.includes(site.last_run_status)) {
    return (
      <Button className="ml-auto" disabled={isLoading} onClick={handleCancelManualScrape}>
        End Manual Collection
      </Button>
    );
  } else {
    return (
      <Button className="ml-auto" disabled={isLoading} onClick={handleRunManualScrape}>
        Start Manual Collection
      </Button>
    );
  }
}

export function CollectionsPage() {
  const [newDocumentModalOpen, setNewDocumentModalOpen] = useState(false);
  const [runScrape] = useRunSiteScrapeTaskMutation();
  const params = useParams();
  const siteId = params.siteId;
  const { data: site, refetch } = useGetSiteQuery(siteId);
  if (!site) return null;

  async function handleRunScrape() {
    if (site?._id) {
      try {
        let response: any = await runScrape(site._id).unwrap();
        if (response.success) {
          if (refetch) refetch();
        } else {
          notification.error({
            message: 'Error Running Collection',
            description: response.error.data.detail,
          });
        }
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
      {newDocumentModalOpen ? (
        <AddDocumentModal setOpen={setNewDocumentModalOpen} siteId={site._id} />
      ) : null}
      <MainLayout
        sidebar={<SiteMenu />}
        sectionToolbar={
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
          siteId={site._id}
          openNewDocumentModal={() => setNewDocumentModalOpen(true)}
        />
      </MainLayout>
    </>
  );
}
