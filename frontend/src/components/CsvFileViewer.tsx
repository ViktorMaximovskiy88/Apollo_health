import { Table } from 'antd';
import { useEffect, useState } from 'react';
import { useGetDocumentViewerUrlQuery } from '../features/retrieved_documents/documentsApi';
import { reduce, compact, camelCase } from 'lodash';

interface CsvFileLoaderPropTypes {
  docId: string | undefined;
}

interface CsvFileViewerPropTypes {
  url: string | undefined;
}

export function CsvFileLoader({ docId }: CsvFileLoaderPropTypes) {
  const { data: viewer } = useGetDocumentViewerUrlQuery(docId);
  return <CsvFileViewer url={viewer?.url} />;
}

export function CsvFileViewer({ url }: CsvFileViewerPropTypes) {
  const [rows, setRows] = useState([] as any[]);
  const [headers, setHeaders] = useState([] as any[]);

  useEffect(() => {
    if (url) {
      fetch(url as string)
        .then((res) => res.text())
        .then((text) => {
          let _rows = text.split('\n').map((row) => {
            return row.match(/\s*("[^"]+"|[^,]+)\s*/gi);
          });

          _rows = compact(_rows);

          const headers = (_rows.shift() || []).map((header: string) => ({
            title: header,
            key: camelCase(header),
            dataIndex: camelCase(header),
          }));

          const rows = _rows.map((cells: any, i: number) => {
            return reduce(
              cells,
              (acc: any, cell: any, j: number) => {
                acc.key = i;
                if (cell) {
                  acc[headers[j].dataIndex] = cell;
                }
                return acc;
              },
              {}
            );
          });

          setHeaders(headers);
          setRows(rows);
        });
    }
  }, [url]);

  if (!url) {
    return <></>;
  }

  return (
    <div data-type="csv" className="flex bg-white h-full overflow-auto">
      <Table dataSource={rows} columns={headers} pagination={false} sticky={true} />
    </div>
  );
}
