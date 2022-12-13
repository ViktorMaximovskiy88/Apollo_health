import { useCallback, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';

import { docDocumentTableState } from '../doc_documents/docDocumentsSlice';
import {
  useGetPayerFamiliesQuery,
  useGetPayerFamilyQuery,
  useLazyGetPayerFamiliesQuery,
} from './payerFamilyApi';
import { SiteDocDocument } from '../doc_documents/types';

export function usePayerFamilySelectOptions(filterName: string) {
  const [getPayerFamilies] = useLazyGetPayerFamiliesQuery();

  const payerFamilyOptions = useCallback(
    async (search: string) => {
      const { data } = await getPayerFamilies({
        limit: 20,
        skip: 0,
        sortInfo: { name: 'name', dir: 1 },
        filterValue: [{ name: 'name', operator: 'contains', type: 'string', value: search }],
      });
      if (!data) return [];
      return data.data.map((pf) => ({ label: pf.name, value: pf._id }));
    },
    [getPayerFamilies]
  );

  const res = useSelector(docDocumentTableState);
  const payerFamilyFilter = res.filter.find((f) => f.name === filterName);
  const { data: payerFamily } = useGetPayerFamilyQuery(payerFamilyFilter?.value ?? undefined, {
    skip: !payerFamilyFilter?.value,
  });
  const initialPayerFamilyOptions = payerFamily
    ? [{ value: payerFamily._id, label: payerFamily.name }]
    : [];
  return { payerFamilyOptions, initialPayerFamilyOptions };
}

export function useGetPayerFamilyNamesById() {
  const [payerFamilyIds, setPayerFamilyIds] = useState<string[]>([]);
  const { data: payerFamilies } = useGetPayerFamiliesQuery({
    limit: 1000,
    skip: 0,
    sortInfo: { name: 'name', dir: 1 },
    filterValue: [{ name: '_id', operator: 'eq', type: 'string', value: payerFamilyIds }],
  });
  const payerFamilyNamesById = useMemo(() => {
    const map: { [key: string]: string } = {};
    payerFamilies?.data.forEach((payerFamily) => {
      map[payerFamily._id] = payerFamily.name;
    });
    return map;
  }, [payerFamilies]);
  return { setPayerFamilyIds, payerFamilyNamesById };
}

export const uniquePayerFamilyIds = (docDocuments: SiteDocDocument[]): string[] => {
  const payerFamilyIds = docDocuments
    .map(({ payer_family_id }) => payer_family_id ?? '')
    .filter(Boolean);
  const usedPayerFamilyIds = new Set(payerFamilyIds);
  return Array.from(usedPayerFamilyIds);
};
