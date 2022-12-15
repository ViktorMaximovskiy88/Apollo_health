import { MainLayout } from '../../components';
import { useParams } from 'react-router-dom';
import { useGetCollectionStatsQuery } from './statsApi';
import { useStatsSlice } from './stats-slice';
import classNames from 'classnames';
import { CollectionChart } from './CollectionChart';

export function CollectionStatsPage() {
  const { siteId } = useParams();

  useGetCollectionStatsQuery(siteId, {
    pollingInterval: 5000,
  });
  const { state } = useStatsSlice();

  return (
    <MainLayout>
      <div className={classNames('flex flex-row h-full')}>
        <CollectionChart collectionStats={state.collectionStats} />
      </div>
    </MainLayout>
  );
}
