import { useState, useEffect } from 'react';
import { Button, Layout} from 'antd';
import { useParams } from 'react-router-dom';
import Title from 'antd/lib/typography/Title';
import { DownOutlined } from '@ant-design/icons';
import { useNavigate } from "react-router-dom";

import { useRunSiteScrapeTaskMutation, useCancelAllSiteScrapeTasksMutation } from './siteScrapeTasksApi';
import { useGetSiteQuery } from '../sites/sitesApi';
import { CollectionsDataTable } from './CollectionsDataTable';
import { CollectionMethod } from '../sites/types';
import { ErrorLogModal } from './ErrorLogModal';
import { SiteStatus } from '../sites/siteStatus';
import { TaskStatus } from "../../common/scrapeTaskStatus";

export function CollectionsPage() {
  const [modalVisible, setModalVisible] = useState(false);
  const [errorTraceback, setErrorTraceback] = useState('');
  const navigate = useNavigate();

  const openErrorModal = (errorTraceback: string): void => {
    setErrorTraceback(errorTraceback);
    setModalVisible(true);
  };

  const params = useParams();
  const siteId = params.siteId;
  const { data: site, refetch } = useGetSiteQuery(siteId);
  const [ runScrape ] = useRunSiteScrapeTaskMutation();
  const [ cancelAllScrapes ] = useCancelAllSiteScrapeTasksMutation();
  if (!siteId) return null;

  async function handleRunScrape(){
    let response: any = await runScrape(site!._id);
    if (response) {
        refetch();
        navigate(`/sites/${site!._id}/documents?scrape_task_id=${response.data._id}`)
    }
  }
  async function handleCancelScrape(){
    await cancelAllScrapes(site!._id);
    refetch();
  }

  return (
    <>
      <ErrorLogModal
        visible={modalVisible}
        setVisible={setModalVisible}
        errorTraceback={errorTraceback}
      />
      <Layout className="bg-white">
        <div className="flex">
          <Title level={4}>Collections</Title>
          {site &&
          site.collection_method === CollectionMethod.Automated &&
          site.status !== SiteStatus.Inactive ? (
            <Button onClick={() => runScrape(site._id)} className="ml-auto">
              Run Collection
            </Button>
          ) : site && site.collection_method === CollectionMethod.Manual && site.status !== SiteStatus.Inactive ? (
            <>
                {
                    site.last_run_status == TaskStatus.Queued || site.last_run_status == TaskStatus.Pending || site.last_run_status == TaskStatus.InProgress ?
                    <Button className="ml-auto" onClick={handleCancelScrape}>
                      End Manual Collection
                    </Button>
                    :
                    <Button className="ml-auto" onClick={handleRunScrape}>
                      Run Manual Collection
                    </Button>
                }
            </>
          )
          :
          null}
        </div>
        <CollectionsDataTable siteId={siteId} openErrorModal={openErrorModal} />
      </Layout>
    </>
  );
}



