import classNames from 'classnames';
import { Button } from 'antd';
import { TextEllipsis } from '../../components';
import { prettyDateUTCFromISO } from '../../common/date';
import { LineageDoc } from './types';

interface PropTypes {
  doc: LineageDoc;
  isSelected: boolean;
  setLeftSide(doc: LineageDoc): void;
  setRightSide(doc: LineageDoc): void;
}

export function LineageDocRow({ isSelected, doc, setLeftSide, setRightSide }: PropTypes) {
  return (
    <div
      key={doc._id}
      className={classNames(
        'p-2 my-2 bg-slate-50 group relative border-slate-200 border border-solid',
        isSelected && ['outline outline-offset-2 outline-1 outline-blue-300']
      )}
    >
      <TextEllipsis text={doc.name} />
      <TextEllipsis text={doc.document_type} />
      <div>{prettyDateUTCFromISO(doc.final_effective_date)}</div>
      <div className="hidden group-hover:block absolute bottom-2 right-2 z-50">
        <Button
          onClick={() => {
            setLeftSide(doc);
          }}
        >
          Left
        </Button>

        <Button
          onClick={() => {
            setRightSide(doc);
          }}
        >
          Right
        </Button>
      </div>
    </div>
  );
}
