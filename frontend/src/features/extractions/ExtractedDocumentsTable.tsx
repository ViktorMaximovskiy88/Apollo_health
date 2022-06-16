import ReactDataGrid from "@inovua/reactdatagrid-community";
import DateFilter from "@inovua/reactdatagrid-community/DateFilter";
import SelectFilter from "@inovua/reactdatagrid-community/SelectFilter";
import { useCallback } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { extractedDocumentTableState, setExtractedDocumentTableFilter, setExtractedDocumentTableSort } from "../../app/uiSlice";
import { prettyDateFromISO } from "../../common";
import { ChangeLogModal } from "../change-log/ChangeLogModal";
import { useGetDocumentsQuery } from "../documents/documentsApi";
import { RetrievedDocument } from "../documents/types";
import { useGetChangeLogQuery } from "./extractionsApi";

const columns = [
    {
      header: 'First Collected',
      name: 'collection_time',
      minWidth: 200,
      filterEditor: DateFilter,
      filterEditorProps: () => {
        return {
          dateFormat: 'YYYY-MM-DD',
          highlightWeekends: false,
          placeholder: 'Select Date'
        }
      },
      render: ({ value: collection_time }: { value: string }) => {
        return prettyDateFromISO(collection_time);
      },
    },
    {
      header: 'Name',
      name: 'name',
      defaultFlex: 1,
      render: ({ data: doc }: { data: RetrievedDocument }) => {
        return <Link to={`document/${doc._id}`}>{doc.name}</Link>;
      },
    },
    {
      header: 'Document Type',
      name: 'document_type',
      minWidth: 200,
      filterEditor: SelectFilter,
      filterEditorProps: { 
        placeholder: 'All',
        dataSource: [
            { id: 'Authorization Policy', label: 'Authorization Policy' },
            { id: 'Provider Guide', label: 'Provider Guide' },
            { d: 'Treatment Request Form', label: 'Treatment Request Form' },
            { id: 'Payer Unlisted Policy', label: 'Payer Unlisted Policy' },
            { id: 'Covered Treatment List', label: 'Covered Treatment List' },
            { id: 'Regulatory Document', label: 'Regulatory Document' },
            { id: 'Formulary', label: 'Formulary' },
            { id: 'Internal Reference', label: 'Internal Reference' },
        ]
      },
      render: ({ value: document_type }: { value: string }) => {
        return <>{document_type}</>;
      },
    },
    {
      header: 'Effective Date',
      name: 'effective_date',
      render: ({ value: effective_date }: { value: string }) => {
        if (!effective_date) return null;
        return prettyDateFromISO(effective_date);
      },
    },
    {
      header: 'Actions',
      name: 'action',
      render: ({ data: doc }: { data: RetrievedDocument }) => {
        return (
          <>
            <ChangeLogModal
              target={doc}
              useChangeLogQuery={useGetChangeLogQuery}
            />
          </>
        );
      },
    },
  ];

export function ExtractedDocumentsTable() {
  const [searchParams] = useSearchParams();
  const params = useParams();
  const scrapeTaskId = searchParams.get('scrape_task_id');
  const siteId = params.siteId;
  const { data: documents } = useGetDocumentsQuery(
    {
      scrape_task_id: scrapeTaskId,
      site_id: siteId,
        automated_content_extraction: true,
    },
    { pollingInterval: 5000 }
  );

  const tableState = useSelector(extractedDocumentTableState)
  const dispatch = useDispatch()
  const onFilterChange = useCallback((filter: any) => dispatch(setExtractedDocumentTableFilter(filter)), [dispatch]);
  const onSortChange = useCallback((sort: any) => dispatch(setExtractedDocumentTableSort(sort)), [dispatch]);

  return (
    <ReactDataGrid
      dataSource={documents || []}
      rowHeight={50}
      columns={columns}
      defaultFilterValue={tableState.filter}
      onFilterValueChange={onFilterChange}
      defaultSortInfo={tableState.sort}
      onSortInfoChange={onSortChange}
    />
  );
}