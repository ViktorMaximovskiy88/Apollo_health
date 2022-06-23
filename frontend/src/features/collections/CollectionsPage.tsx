import { useState } from 'react';
import { Button, Layout } from 'antd';
import { useParams } from 'react-router-dom';
import { useRunSiteScrapeTaskMutation } from './siteScrapeTasksApi';
import Title from 'antd/lib/typography/Title';
import { CollectionsDataTable } from './CollectionsDataTable';
import { ErrorLogModal } from './ErrorLogModal';

export function CollectionsPage() {
  const [modalVisible, setModalVisible] = useState(false);
  const [errorTraceback, setErrorTraceback] = useState('');

  const openErrorModal = (errorTraceback: string): void => {
    setErrorTraceback(errorTraceback);
    setModalVisible(true);
  };

  const params = useParams();
  const siteId = params.siteId;
  const [runScrape] = useRunSiteScrapeTaskMutation();
  if (!siteId) return null;

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
          <Button onClick={() => runScrape(siteId)} className="ml-auto">
            Run Collection
          </Button>
        </div>
        <CollectionsDataTable siteId={siteId} openErrorModal={openErrorModal} />
      </Layout>
    </>
  );
}
