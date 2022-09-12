import { Button, Input, InputNumber, Switch, Tag } from 'antd';
import { CheckOutlined, CloseOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { VirtualItem } from '@tanstack/react-virtual';
import { DocumentTag, TherapyTag } from './types';

function labelColorMap(type: string) {
  const colorMap: any = {
    indication: 'blue',
    therapy: 'green',
    'therapy-group': 'purple',
  };
  return colorMap[type];
}

export function EditTag({
  onEditTag,
  onToggleEdit,
  tag,
  virtualRow,
}: {
  onDeleteTag: Function;
  onEditTag: Function;
  onToggleEdit: Function;
  tag: DocumentTag;
  virtualRow: VirtualItem<unknown>;
}) {
  let focus = false;
  if (tag._type === 'therapy') {
    focus = (tag as TherapyTag).focus;
  }

  return (
    <div
      className="flex flex-col justify-center"
      style={{
        borderTop: '1px solid #ccc',
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: `${virtualRow.size}px`,
        transform: `translateY(${virtualRow.start}px)`,
      }}
      ref={virtualRow.measureElement}
    >
      <div className="flex">
        <Input
          defaultValue={tag.name}
          id="name"
          onChange={(e) => onEditTag(tag.id, 'name', e.target.value)}
          placeholder="Name"
          size="small"
          className="flex w-56 max-h-6"
        />
      </div>
      <div className="flex items-center">
        <Input
          defaultValue={tag.text}
          id="text"
          onChange={(e) => onEditTag(tag.id, 'text', e.target.value)}
          placeholder="Text"
          size="small"
          className="flex items-center max-h-6"
        />
        {tag._type === 'therapy' && (
          <div className="flex-1 items-center px-5">
            <Switch
              defaultChecked={focus}
              id="focus"
              onChange={(checked) => onEditTag(tag.id, 'focus', checked)}
              checkedChildren="Focus"
              unCheckedChildren="Focus"
            />
          </div>
        )}
        <InputNumber
          controls={false}
          defaultValue={tag.page + 1}
          id="page"
          onChange={(page) => onEditTag(tag.id, 'page', page)}
          min={0}
          size="small"
          className="flex min-w-min items-center mr-3"
        />
        <div className="flex items-center w-32 justify-center">
          <Tag color={labelColorMap(tag._type)} className="capitalize select-none cursor-default">
            {tag._type}
          </Tag>
        </div>
        <div className="flex justify-center space-x-2">
          <Button onClick={() => onToggleEdit(tag, false)}>
            <CheckOutlined className="cursor-pointer" />
          </Button>

          <Button onClick={() => onToggleEdit(tag, false, true)}>
            <CloseOutlined className="cursor-pointer" />
          </Button>
        </div>
      </div>
    </div>
  );
}

export function ReadTag({
  onToggleEdit,
  onDeleteTag,
  tag,
  virtualRow,
}: {
  onToggleEdit: Function;
  onDeleteTag: Function;
  tag: DocumentTag;
  virtualRow: VirtualItem<unknown>;
}) {
  let focus = false;
  if (tag._type === 'therapy') {
    focus = (tag as TherapyTag).focus;
  }
  return (
    <div
      className="flex flex-col py-2 justify-center"
      style={{
        borderTop: '1px solid #ccc',
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: `${virtualRow.size}px`,
        transform: `translateY(${virtualRow.start}px)`,
      }}
      ref={virtualRow.measureElement}
    >
      <div className="flex">
        <div className="flex flex-1 font-bold">{tag.name}</div>
      </div>
      <div className="flex">
        <div className="flex items-center flex-1">{tag.text}</div>
        <div className="flex items-center px-5">
          {focus && (
            <Tag color="gold" className="select-none cursor-default">
              Focus
            </Tag>
          )}
        </div>
        <div className="flex items-center px-2">{tag.page + 1}</div>
        <div className="flex items-center w-32 justify-center">
          <Tag color={labelColorMap(tag._type)} className="capitalize select-none cursor-default">
            {tag._type}
          </Tag>
        </div>
        <div className="flex justify-center space-x-2">
          <Button
            onClick={() => {
              onToggleEdit(tag, true);
            }}
          >
            <EditOutlined className="cursor-pointer" />
          </Button>

          <Button
            onClick={() => {
              onDeleteTag(tag);
            }}
          >
            <DeleteOutlined className="cursor-pointer" />
          </Button>
        </div>
      </div>
    </div>
  );
}
