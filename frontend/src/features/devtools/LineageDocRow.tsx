import classNames from 'classnames';
import { Button } from 'antd';
import { SplitCellsOutlined } from '@ant-design/icons';
import { TextEllipsis } from '../../components';
import { prettyDateUTCFromISO } from '../../common/date';
import { LineageDoc } from './types';

interface PropTypes {
  doc: LineageDoc;
  isSelected: boolean;
  enableSplitView: boolean;
  setViewItem(doc: LineageDoc): void;
  setSplitItem(doc: LineageDoc): void;
}

export function LineageDocRow({
  isSelected,
  doc,
  enableSplitView,
  setViewItem,
  setSplitItem,
}: PropTypes) {
  return (
    <div
      key={doc._id}
      className={classNames(
        'p-2 my-2 bg-slate-50 group relative border-slate-200 border border-solid cursor-pointer',
        isSelected && ['outline outline-offset-2 outline-1 outline-blue-300']
      )}
    >
      <div
        className={classNames('cursor-pointer')}
        onClick={() => {
          setViewItem(doc);
        }}
      >
        <TextEllipsis text={doc.name} />
        <TextEllipsis text={doc.document_type} />
        <div>{prettyDateUTCFromISO(doc.final_effective_date)}</div>
      </div>
      <div className="hidden group-hover:block absolute bottom-2 right-2 z-50">
        {enableSplitView && (
          <Button
            onClick={() => {
              setSplitItem(doc);
            }}
          >
            <SplitCellsOutlined />
          </Button>
        )}
      </div>
    </div>
  );
}
