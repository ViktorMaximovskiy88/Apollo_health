import ReactDataGrid from '@inovua/reactdatagrid-community';
import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { Dispatch, SetStateAction, useCallback, useContext, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { prettyDateFromISO } from '../../../common';
import { ButtonLink, GridPaginationToolbar } from '../../../components';
import { useGetDocDocumentQuery, useLazyGetDocDocumentsQuery } from '../docDocumentApi';
import { DocDocument } from '../types';
import { useInterval } from '../../../common/hooks';
import { DocumentTypes } from '../../retrieved_documents/types';
import { TypePaginationProps } from '@inovua/reactdatagrid-community/types';
import { useDataTableSort } from '../../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../../common/hooks/use-data-table-filter';
import { useParams } from 'react-router-dom';
import {
  lineageDocDocumentTableState,
  setLineageDocDocumentTableFilter,
  setLineageDocDocumentTableLimit,
  setLineageDocDocumentTableSkip,
  setLineageDocDocumentTableSort,
} from './lineageDocDocumentsSlice';
import { PreviousDocDocContext } from './PreviousDocDocContext';

const createColumns = ({
  previousDocDocumentId,
  setPreviousDocDocumentId,
}: {
  previousDocDocumentId: string;
  setPreviousDocDocumentId: Dispatch<SetStateAction<string>>;
}) => [
  {
    header: 'Name',
    name: 'name',
    render: ({ data: doc }: { data: DocDocument }) => {
      if (doc._id === previousDocDocumentId) {
        return <div className="ml-2">{doc.name}</div>;
      }
      return <ButtonLink onClick={() => setPreviousDocDocumentId(doc._id)}>{doc.name}</ButtonLink>;
    },
    defaultFlex: 1,
    minWidth: 300,
  },
  {
    header: 'Document Type',
    name: 'document_type',
    minWidth: 200,
    filterEditor: SelectFilter,
    filterEditorProps: {
      placeholder: 'All',
      dataSource: DocumentTypes,
    },
    render: ({ value: document_type }: { value: string }) => {
      return <>{document_type}</>;
    },
  },
  {
    header: 'Final Effective Date',
    name: 'final_effective_date',
    minWidth: 200,
    filterEditor: DateFilter,
    filterEditorProps: () => {
      return {
        dateFormat: 'YYYY-MM-DD',
        highlightWeekends: false,
        placeholder: 'Select Date',
      };
    },
    render: ({ value: final_effective_date }: { value: string }) => (
      <>{prettyDateFromISO(final_effective_date)}</>
    ),
  },
];

export const useLineageDocDocumentColumns = () => {
  const [previousDocDocumentId, setPreviousDocDocumentId] = useContext(PreviousDocDocContext);

  return useMemo(
    () => createColumns({ previousDocDocumentId, setPreviousDocDocumentId }),
    [previousDocDocumentId, setPreviousDocDocumentId]
  );
};
