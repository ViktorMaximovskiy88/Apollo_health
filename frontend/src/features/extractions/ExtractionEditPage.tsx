import { Table } from 'antd';
import Title from 'antd/lib/typography/Title';
import { useParams } from 'react-router-dom';
import { useGetExtractionTaskResultsQuery } from './extractionsApi';
import { ContentExtractionResult } from './types';

export function ExtractionEditPage() {
  const { docId, siteId, extractionId } = useParams();
  const { data: extractions } = useGetExtractionTaskResultsQuery(extractionId);

  if (!extractions) return null;

  const firstRow = extractions[0];
  const header = Object.keys((firstRow || {result: []}).result);
  const columns = [
    {
      title: 'Page',
      key: 'page',
      render: (res: ContentExtractionResult) => {
        return <>{res.page}</>;
      },
    },
    {
      title: 'Row',
      key: 'row',
      render: (res: ContentExtractionResult) => {
        return <>{res.row}</>;
      },
    },
  ].concat(
    header.map((h) => ({
      title: h,
      key: h,
      render: (res: ContentExtractionResult) => {
        const data: any = res.result;
        return <>{data[h]}</>;
      },
    }))
  );

  return (
    <div>
      <div className="flex">
        <Title className="inline-block" level={4}>
          Extraction Results
        </Title>
      </div>
      <Table
        dataSource={extractions}
        columns={columns}
        rowKey={(doc) => doc._id}
      />
    </div>
  );
}
