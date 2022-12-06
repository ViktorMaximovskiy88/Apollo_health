import { useCallback, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import { docDocumentTableState } from '../docDocumentsSlice';
import { DocDocument, SiteDocDocument } from '../types';
import {
  useGetDocumentFamiliesQuery,
  useGetDocumentFamilyQuery,
  useLazyGetDocumentFamiliesQuery,
} from './documentFamilyApi';

const buildFilterValue = (search: string, siteId?: string) => {
  const filterValue = [{ name: 'name', operator: 'contains', type: 'string', value: search }];
  if (!siteId) {
    return filterValue;
  }
  return [...filterValue, { name: 'site_ids', operator: 'eq', type: 'string', value: siteId }];
};

export function useDocumentFamilySelectOptions() {
  const { siteId } = useParams();
  const [getDocumentFamilies] = useLazyGetDocumentFamiliesQuery();

  const documentFamilyOptions = useCallback(
    async (search: string) => {
      const filterValue = buildFilterValue(search, siteId);
      const { data } = await getDocumentFamilies({
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue,
      });
      if (!data) return [];
      return data.data.map((df) => ({ label: df.name, value: df._id }));
    },
    [getDocumentFamilies, siteId]
  );

  const res = useSelector(docDocumentTableState);
  const documentFamilyFilter = res.filter.find((f) => f.name === 'document_family_id');
  const { data: documentFamily } = useGetDocumentFamilyQuery(
    documentFamilyFilter?.value ?? undefined,
    { skip: !documentFamilyFilter?.value }
  );
  const initialDocumentFamilyOptions = documentFamily
    ? [{ value: documentFamily._id, label: documentFamily.name }]
    : [];

  return { documentFamilyOptions, initialDocumentFamilyOptions };
}

export function useGetDocumentFamilyNamesById() {
  const [documentFamilyIds, setDocumentFamilyIds] = useState<string[]>([]);
  const { data: documentFamilies } = useGetDocumentFamiliesQuery({
    limit: 1000,
    skip: 0,
    sortInfo: { name: 'name', dir: 1 },
    filterValue: [{ name: '_id', operator: 'eq', type: 'string', value: documentFamilyIds }],
  });
  const documentFamilyNamesById = useMemo(() => {
    const map: { [key: string]: string } = {};
    documentFamilies?.data.forEach((documentFamily) => {
      map[documentFamily._id] = documentFamily.name;
    });
    return map;
  }, [documentFamilies]);
  return { setDocumentFamilyIds, documentFamilyNamesById };
}

export const uniqueDocumentFamilyIds = (
  docDocuments: (DocDocument | SiteDocDocument)[]
): string[] => {
  const documentFamilyIds = docDocuments
    .map(({ document_family_id }) => document_family_id ?? '')
    .filter(Boolean);
  const usedDocumentFamilyIds = new Set(documentFamilyIds);
  return Array.from(usedDocumentFamilyIds);
};
