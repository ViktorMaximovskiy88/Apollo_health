import DateFilter from '@inovua/reactdatagrid-community/DateFilter';
import SelectFilter from '@inovua/reactdatagrid-community/SelectFilter';
import { useCallback, useMemo } from 'react';
import { prettyDateUTCFromISO } from '../../../common';
import { ButtonLink } from '../../../components';
import { DocDocument } from '../types';
import { DocumentTypes } from '../../retrieved_documents/types';
import { useSelector } from 'react-redux';
import { previousDocDocumentIdState, setPreviousDocDocumentId } from './lineageDocDocumentsSlice';
import { useAppDispatch } from '../../../app/store';

export const useLineageDocDocumentColumns = () => {
  const dispatch = useAppDispatch();
  const previousDocDocumentId = useSelector(previousDocDocumentIdState);
  const handlePreviousDocDocumentChange = useCallback(
    (id: string) => dispatch(setPreviousDocDocumentId(id)),
    [dispatch]
  );
  return useMemo(
    () => [
      {
        header: 'Name',
        name: 'name',
        render: ({ data: doc }: { data: DocDocument }) => {
          if (doc._id === previousDocDocumentId) {
            return <div className="ml-2">{doc.name}</div>;
          }
          return (
            <ButtonLink onClick={() => handlePreviousDocDocumentChange(doc._id)}>
              {doc.name}
            </ButtonLink>
          );
        },
        defaultFlex: 1,
        minWidth: 300,
      },
      {
        header: 'Link Text',
        name: 'locations.link_text',
        render: ({ data: docDocument }: { data: DocDocument }) => {
          const linkTexts = docDocument.locations.map((location) => location.link_text);
          return <>{linkTexts.join(', ')}</>;
        },
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
          <>{prettyDateUTCFromISO(final_effective_date)}</>
        ),
      },
    ],
    [handlePreviousDocDocumentChange, previousDocDocumentId]
  );
};
