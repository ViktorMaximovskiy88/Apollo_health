import { Button, Form, Tabs, Image } from 'antd';
import { Viewer, Worker } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { FormInstance } from 'antd/lib/form/Form';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useGetDocDocumentQuery } from '../doc_documents/docDocumentApi';
import { RetrievedDocumentViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import { useAccessToken } from '../../common/hooks';
import { baseApiUrl, fetchWithAuth } from '../../app/base-api';
import ReactDataGrid from '@inovua/reactdatagrid-community';
import { TypeColumn } from '@inovua/reactdatagrid-community/types';
import { ColumnTranslation } from './types';
import { sortBy, uniqBy } from 'lodash';
import {
  useExtractSampleDocumentTablesQuery,
  useTranslateSampleDocumentTablesQuery,
} from './translationApi';

export function TranslationTestingDocumentPreview(props: { docId?: string }) {
  const { data: doc } = useGetDocDocumentQuery(props.docId, { skip: !props.docId });
  if (!doc) return null;

  return (
    <div className="overflow-auto">
      <RetrievedDocumentViewer docId={doc.retrieved_document_id} doc={doc} />
    </div>
  );
}

export function TranslationDocumentSampler(props: { form: FormInstance<any>; docId: string }) {
  const token = useAccessToken();
  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  const [config, setConfig] = useState(props.form.getFieldsValue());
  const configStr = encodeURIComponent(JSON.stringify(config));

  const onClick = useCallback(() => {
    setConfig(props.form.getFieldsValue());
  }, [setConfig, props]);

  return (
    <div className="flex flex-col h-full px-4">
      <SampleActionButton onClick={onClick} text="Generate Sample Document" />
      <div className="overflow-auto">
        <Worker workerUrl="/pdf.worker.min.js">
          <Viewer
            withCredentials={true}
            fileUrl={`${baseApiUrl}/translations/sample-doc/${props.docId}?config=${configStr}`}
            plugins={[defaultLayoutPluginInstance]}
            httpHeaders={{
              Authorization: `Bearer ${token}`,
            }}
          />
        </Worker>
      </div>
    </div>
  );
}

function TranslationTableExtractionSample(props: { form: FormInstance<any>; docId: string }) {
  const [imgBlob, setImgBlob] = useState<string | undefined>();

  const [config, setConfig] = useState(props.form.getFieldsValue());

  const onClick = useCallback(() => {
    setConfig(props.form.getFieldsValue());
  }, [setConfig, props]);

  useEffect(() => {
    (async () => {
      const configStr = encodeURIComponent(JSON.stringify(config));
      const response = await fetchWithAuth(
        `${baseApiUrl}/translations/sample-doc/${config.sample.doc_id}/table-image?config=${configStr}`
      );
      if (response.ok) {
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        setImgBlob(blobUrl);
      }
    })();
  }, [config, setImgBlob]);

  return (
    <div className="flex flex-col h-full px-4">
      <SampleActionButton onClick={onClick} text="Identify Table Cells" />
      {imgBlob && (
        <div className="overflow-auto">
          <Image preview={false} src={imgBlob} />
        </div>
      )}
    </div>
  );
}

export function SampleTranslationTable(props: { docId: string; form: FormInstance<any> }) {
  const [config, setConfig] = useState(props.form.getFieldsValue());
  const { data, isFetching } = useTranslateSampleDocumentTablesQuery(config, {
    skip: !config,
  });
  const onClick = useCallback(() => {
    setConfig(props.form.getFieldsValue());
  }, [setConfig, props]);

  const columns: TypeColumn[] = useMemo(() => {
    const columnRules: ColumnTranslation[] = config.translation?.column_rules ?? [];
    const translationRules = columnRules.flatMap((cr) => cr.rules);
    const newColumns = translationRules.flatMap((col): TypeColumn[] => {
      const cols: TypeColumn[] = [];
      if (col.field === 'Brand' || col.field === 'Generic') {
        cols.push({
          header: 'Name',
          name: 'name',
          defaultFlex: 1,
          minWidth: 300,
        });
        cols.push({
          header: 'Code',
          name: 'code',
          minWidth: 80,
          width: 80,
        });
        cols.push({
          header: 'RxNorm',
          name: 'rxcui',
          minWidth: 100,
          width: 100,
        });
      } else if (col.field === 'Tier') {
        cols.push({
          header: 'Tier',
          name: 'tier',
          minWidth: 70,
          maxWidth: 70,
        });
      } else if (col.field === 'SP') {
        cols.push({
          header: 'SP',
          render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
          name: 'sp',
          minWidth: 62,
          maxWidth: 62,
        });
      } else if (col.field === 'ST') {
        cols.push({
          header: 'ST',
          render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
          name: 'st',
          minWidth: 62,
          maxWidth: 62,
        });
        if (col.capture_all || col.pattern.includes('*')) {
          cols.push({
            header: 'ST Note',
            minWidth: 100,
            name: 'stn',
          });
        }
      } else if (col.field === 'PA') {
        cols.push({
          header: 'PA',
          render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
          name: 'pa',
          minWidth: 62,
          maxWidth: 62,
        });
        if (col.capture_all || col.pattern.includes('*')) {
          cols.push({
            header: 'PA Note',
            minWidth: 100,
            name: 'pan',
          });
        }
      } else if (col.field === 'CPA') {
        cols.push({
          header: 'CPA',
          render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
          name: 'cpa',
          minWidth: 62,
          maxWidth: 62,
        });
        if (col.capture_all || col.pattern.includes('*')) {
          cols.push({
            header: 'Cond. PA Note',
            minWidth: 100,
            name: 'cpan',
          });
        }
      } else if (col.field === 'QL' || col.field === 'QLC') {
        cols.push({
          header: 'QL',
          render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
          name: 'ql',
          minWidth: 63,
          maxWidth: 63,
        });
        if (col.capture_all || col.pattern.includes('*') || col.field === 'QLC') {
          cols.push({
            header: 'QL Note',
            name: 'qln',
            minWidth: 100,
          });
        }
      } else if (col.field === 'STPA') {
        cols.push({
          header: 'STPA',
          name: 'stpa',
          render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
          minWidth: 62,
          maxWidth: 62,
        });
      } else if (col.field === 'MB') {
        cols.push({
          header: 'MB',
          name: 'mb',
          render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
          minWidth: 70,
          maxWidth: 70,
        });
      } else if (col.field === 'SCO') {
        cols.push({
          header: 'SCO',
          name: 'sco',
          render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
          minWidth: 100,
          maxWidth: 100,
        });
      } else if (col.field === 'DME') {
        cols.push({
          header: 'DME',
          name: 'dme',
          render: ({ value }: { value: boolean }) => (value ? 'True' : ''),
          minWidth: 70,
        });
      } else if (col.field === 'PN') {
        cols.push({
          header: 'PN',
          name: 'pn',
          minWidth: 70,
        });
      }
      return cols;
    });
    const order = [
      'name',
      'code',
      'rxcui',
      'tier',
      'sp',
      'st',
      'stn',
      'pa',
      'pn',
      'pan',
      'cpa',
      'cpan',
      'stpa',
      'mb',
      'sco',
      'dme',
      'ql',
      'qln',
    ];
    return sortBy(uniqBy(newColumns, 'name'), (c) => order.indexOf(c.name!));
  }, [config]);

  return (
    <div className="flex px-4 flex-col h-full">
      <SampleActionButton onClick={onClick} text="Translate" />
      {
        <ReactDataGrid
          loading={isFetching}
          dataSource={data || []}
          columns={columns}
          columnUserSelect
        />
      }
    </div>
  );
}

function SampleActionButton(props: { onClick: () => void; text: string }) {
  return (
    <div className="mb-4">
      <Button className="w-full" onClick={props.onClick}>
        {props.text}
      </Button>
    </div>
  );
}

export function SampleExtractionTable(props: { docId: string; form: FormInstance<any> }) {
  const [config, setConfig] = useState(props.form.getFieldsValue());
  const { data, isFetching } = useExtractSampleDocumentTablesQuery(config, {
    skip: !config,
    refetchOnMountOrArgChange: true,
  });
  const explicitHeaders = config.extraction.explicit_headers;

  const { tables, columns } = useMemo(() => {
    const tables: string[][][] = [];
    const columns: TypeColumn[][] = [];
    data?.forEach((table) => {
      const newTable: string[][] = [];
      const header: TypeColumn[] = [];
      if ((explicitHeaders || []).length > 0) {
        explicitHeaders.forEach((h: any) => {
          header.push({
            name: h,
            defaultFlex: 1,
            minWidth: 200,
            header: h,
          });
        });
      }
      table.forEach((row, i) => {
        if ((explicitHeaders || []).length === 0 && i === 0) {
          row.forEach((h) =>
            header.push({
              name: h,
              defaultFlex: 1,
              minWidth: 200,
              header: h,
            })
          );
        } else {
          const line: any = {};
          header.forEach((h, i) => {
            line[h.header] = row[i];
          });
          newTable.push(line);
        }
      });
      tables.push(newTable);
      columns.push(header);
    });
    return { tables, columns };
  }, [data, explicitHeaders]);

  const onClick = useCallback(() => {
    setConfig(props.form.getFieldsValue());
  }, [setConfig, props]);

  return (
    <div className="flex flex-col h-full px-4">
      <SampleActionButton onClick={onClick} text="Extract" />
      {tables.length > 0 && (
        <ReactDataGrid
          loading={isFetching}
          dataSource={tables.flat()}
          columns={columns[0]}
          columnUserSelect
        />
      )}
    </div>
  );
}

export function TranslationDocPreview(props: { form: FormInstance<any> }) {
  const docId = Form.useWatch(['sample', 'doc_id'], props.form);

  const items = [
    {
      label: 'Document',
      key: 'document',
      children: (
        <div className="flex flex-col h-full">
          <TranslationTestingDocumentPreview docId={docId} />
        </div>
      ),
    },
  ];

  if (docId) {
    items.push(
      {
        label: 'Document Sample',
        key: 'sample',
        children: <TranslationDocumentSampler form={props.form} docId={docId} />,
      },
      {
        label: 'Table Identification',
        key: 'table-ident',
        children: <TranslationTableExtractionSample form={props.form} docId={docId} />,
      },
      {
        label: 'Extraction',
        key: 'extraction',
        children: <SampleExtractionTable docId={docId} form={props.form} />,
      },
      {
        label: 'Translation',
        key: 'translation',
        children: <SampleTranslationTable docId={docId} form={props.form} />,
      }
    );
  }

  return <Tabs className="h-full ant-tabs-h-full" items={items} />;
}
