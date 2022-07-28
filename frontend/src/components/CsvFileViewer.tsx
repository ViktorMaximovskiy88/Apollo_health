import { useEffect, useState } from 'react';
import { useGetDocumentViewerUrlQuery } from '../features/retrieved_documents/documentsApi';

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
  let colWidth = 0;

  useEffect(() => {
    fetch(url as string)
      .then((res) => res.text())
      .then((text) => {
        // temp csv viewer (pretty dumb)
        // doesnt handle escaped etc... WIP really naive
        const _rows = text.split('\n').map((row) => {
          const cols = row.split(',');
          colWidth = cols.length; // maybe not right could be sparse
          return cols;
        });

        setRows(_rows);
      });
  }, [url]);

  if (!url) {
    return <></>;
  }

  return (
    <div data-type="csv" className="bg-white p-8 border border-gray-200">
      {rows.map((cols: any) => (
        <div>
          {cols.map((cell: any) => (
            <div>{cell}</div>
          ))}
        </div>
      ))}
    </div>
  );
}
