import ReactDataGrid from '@inovua/reactdatagrid-community';
import Title from 'antd/lib/typography/Title';
import { useParams } from 'react-router-dom';
import { useGetExtractionTaskResultsQuery } from './extractionsApi';

export function ExtractionEditPage() {
  const { extractionId } = useParams();
  const { data: extractions } = useGetExtractionTaskResultsQuery(extractionId);

  if (!extractions) return null;

  const firstRow = extractions[0];
  const header = Object.keys((firstRow || { result: [] }).result);
  const columns = [
    {
      header: 'Page',
      name: 'page',
    },
    {
      header: 'Row',
      name: 'row',
    },
  ].concat(
    header.map((h) => ({
      header: h,
      name: h,
      defaultFlex: 1,
    }))
  );
  
  const defaultFilterValue = header.map((name) => ({ name, operator: 'contains', type: 'string', value: '' }));
  const formattedExtractions = extractions.map(({ page, row, result }) => ({ page, row, ...result }))

  return (
    <>
      <div className="flex">
        <Title className="inline-block" level={4}>
          Extraction Results
        </Title>
      </div>
      <ReactDataGrid
        dataSource={formattedExtractions}
        columns={columns}
        rowHeight={50}
        defaultFilterValue={defaultFilterValue}
      />
    </>
  );
}
