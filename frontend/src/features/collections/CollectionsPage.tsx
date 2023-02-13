import { useState } from 'react';
import { Button, notification } from 'antd';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import {
  useRunSiteScrapeTaskMutation,
  useCancelAllSiteScrapeTasksMutation,
  useLazyGetScrapeTaskQuery,
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
import { useAppDispatch } from '../../app/store';
import { setSiteDocDocumentTableForceUpdate } from '../doc_documents/siteDocDocumentsSlice';
import { SiteDocDocument } from '../doc_documents/types';
import { WorkItem, WorkItemOption } from './types';

export function ManualCollectionButton(props: any) {
  const { site, refetch, runScrape, siteScrapeTask, setSiteScrapeTask } = props;
  const navigate = useNavigate();
  const [cancelAllScrapes] = useCancelAllSiteScrapeTasksMutation();
  const [isLoading, setIsLoading] = useState(false);
  const [searchParams] = useSearchParams();
  const scrapeTaskId = searchParams.get('scrape_task_id');
  const activeStatuses = [TaskStatus.Queued, TaskStatus.Pending, TaskStatus.InProgress];
  const [getDocDocumentsQuery] = useLazyGetSiteDocDocumentsQuery();
  const [getScrapeTaskQuery] = useLazyGetScrapeTaskQuery();
  const dispatch = useAppDispatch();
  const [currentDocs, setCurrentDocs] = useState<Array<SiteDocDocument | undefined>>();
  const [initialRefreshDocs, setInitialRefreshDocs] = useState(false);

  const refreshDocs = async () => {
    if (!site) return;
    const siteId = site._id;
    refetch();
    const refreshedDocs = await getDocDocumentsQuery({ siteId, scrapeTaskId });
    setCurrentDocs(refreshedDocs.data?.data);
    dispatch(setSiteDocDocumentTableForceUpdate());
    const { data: refreshedSiteScrapeTask } = await getScrapeTaskQuery(scrapeTaskId);
    if (refreshedSiteScrapeTask && setSiteScrapeTask) {
      setSiteScrapeTask(refreshedSiteScrapeTask);
    }
  };

  if ((!siteScrapeTask && scrapeTaskId) || !initialRefreshDocs) {
    setInitialRefreshDocs(true);
    refreshDocs();
  }

  async function handleRunManualScrape() {
    try {
      setIsLoading(true);
      let response: any = await runScrape(site!._id);
      if (response.data.success) {
        navigate(`../doc-documents?scrape_task_id=${response.data.nav_id}`);
        refreshDocs();
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
    if (siteScrapeTask && siteScrapeTask.work_list) {
      // Check if any unhandled work_items before submitting to backend..
      const unhandled = siteScrapeTask.work_list.filter(
        (work_item: any) => work_item.selected === WorkItemOption.Unhandled
      );
      const unhandledDocNames: (string | undefined)[] = [];
      unhandled?.map((unhandledDoc: WorkItem) =>
        unhandledDocNames.push(
          currentDocs?.filter(
            (doc: SiteDocDocument | undefined) => doc?._id === unhandledDoc.document_id
          )[0]?.name
        )
      );
      if (unhandledDocNames.length > 0) {
        notification.error({
          message: 'Please review and update the following documents ',
          description: unhandledDocNames.map((name) => (
            <>
              {name}
              <br />
            </>
          )),
        });
        return;
      }

      // Stop the collection and refresh docs table.
      if (site?._id) {
        try {
          setIsLoading(true);
          let response: any = await cancelAllScrapes(site!._id);
          if (response.data?.success) {
            refreshDocs();
            setIsLoading(false);
          } else {
            setIsLoading(false);
            notification.error({
              message: 'Please review and update the following documents',
              description: response.data.errors.map((err: any) => (
                <>
                  {err}
                  <br />
                </>
              )),
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
  }

  if (
    site.collection_method === 'MANUAL' &&
    activeStatuses.includes(site.last_run_status) &&
    scrapeTaskId
  ) {
    return (
      <Button className="ml-auto" disabled={isLoading} onClick={handleCancelManualScrape}>
        End Manual Collection
      </Button>
    );
  } else {
    if (site.collection_method === 'MANUAL' && !activeStatuses.includes(site.last_run_status)) {
      return (
        <Button className="ml-auto" disabled={isLoading} onClick={handleRunManualScrape}>
          Start Manual Collection
        </Button>
      );
    } else {
      return null;
    }
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
          refetch();
        } else {
          notification.error({
            message: 'Error Running Collection',
            description: response.errors.join(', '),
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
          site={site}
          openNewDocumentModal={() => setNewDocumentModalOpen(true)}
        />
      </MainLayout>
    </>
  );
}
