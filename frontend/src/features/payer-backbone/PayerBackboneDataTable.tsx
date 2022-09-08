import { useCallback, useMemo } from 'react';
import ReactDataGrid from '@inovua/reactdatagrid-community';
import { ButtonLink } from '../../components';
import { PayerBackbone } from './types';
import {
  setPayerBackboneTableFilter,
  setPayerBackboneTableSort,
  setPayerBackboneTableLimit,
  setPayerBackboneTableSkip,
  payerBackboneTableState,
} from './payerBackboneSlice';
import { useDataTableFilter, useDataTablePagination, useDataTableSort } from '../../common/hooks';
import { useLazyGetPayerBackbonesQuery } from './payerBackboneApi';
import { useParams } from 'react-router-dom';

export function PayerBackboneDataTable() {
  const { payerType } = useParams();
  const [getPayerBackbonesFn] = useLazyGetPayerBackbonesQuery();

  const loadData = useCallback(
    async (tableInfo: any) => {
      const { data } = await getPayerBackbonesFn({ ...tableInfo, type: payerType });
      const sites = data?.data ?? [];
      const count = data?.total ?? 0;
      return { data: sites, count };
    },
    [payerType, getPayerBackbonesFn]
  );

  const columns = useMemo(() => {
    return [
      {
        header: 'Name',
        name: 'name',
        defaultFlex: 1,
        render: ({ data: payer }: { data: PayerBackbone }) => {
          return <ButtonLink to={`${payer._id}`}>{payer.name}</ButtonLink>;
        },
      },
    ];
  }, []);

  const filterProps = useDataTableFilter(payerBackboneTableState, setPayerBackboneTableFilter);
  const sortProps = useDataTableSort(payerBackboneTableState, setPayerBackboneTableSort);
  const paginationProps = useDataTablePagination(
    payerBackboneTableState,
    setPayerBackboneTableLimit,
    setPayerBackboneTableSkip
  );

  if (!payerType) return null;

  return (
    <ReactDataGrid
      dataSource={loadData}
      {...filterProps}
      {...sortProps}
      {...paginationProps}
      columns={columns}
      rowHeight={50}
      activateRowOnFocus={false}
      renderLoadMask={() => <></>}
    />
  );
}
