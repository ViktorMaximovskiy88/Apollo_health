import PaginationToolbar from '@inovua/reactdatagrid-community/packages/PaginationToolbar';
import { Switch } from 'antd';

interface PropTypes {
  paginationProps: any;
  autoRefreshClick: any;
  autoRefreshValue: boolean;
}
/**
 * Grid page footer with auto-refresh toggle
 * @param param0
 * @returns
 */
export function GridPaginationToolbar({
  paginationProps,
  autoRefreshClick,
  autoRefreshValue,
}: PropTypes) {
  return (
    <div className="flex flex-col">
      <PaginationToolbar
        {...paginationProps}
        bordered={false}
        style={{ width: 'fit-content' }}
        onClick={() => {
          autoRefreshClick(false);
        }}
      />
      <div
        className="flex justify-end items-end box-border leading-[2.5rem] h-[42px]"
        style={{
          borderTop: '2px solid #e4e3e2',
        }}
      >
        <div className="mx-4">
          <label className="cursor-pointer select-none">
            <Switch
              defaultChecked={autoRefreshValue}
              checked={autoRefreshValue}
              onChange={(value: boolean) => {
                autoRefreshClick(value);
              }}
            />
            &nbsp;&nbsp;Auto-refresh
          </label>
        </div>
      </div>
    </div>
  );
}
