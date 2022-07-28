import { useEffect, useState, useRef } from 'react';
import { Button, Radio, Tag, Checkbox, Input } from 'antd';
import { DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { debounce, orderBy } from 'lodash';
import { useVirtualizer } from '@tanstack/react-virtual';
import { TherapyTag, IndicationTag } from './types';

function labelColorMap(type: string) {
  const colorMap: any = {
    indication: 'blue',
    therapy: 'green',
    'therapy-group': 'purple',
  };
  return colorMap[type];
}

export function DocDocumentTagForm(props: {
  tags: Array<TherapyTag | IndicationTag>;
  onDeleteTag: Function;
  onEditTag: Function;
  onAddTag: Function;
  currentPage: number;
}) {
  const { tags, onEditTag, onAddTag, onDeleteTag, currentPage } = props;
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredList, setFilteredList] = useState(tags);
  const [tagTypeFilter, setTagTypeFilter] = useState(['indication', 'therapy', 'therapy-group']);
  const [pageFilter, setPageFilter] = useState('page');

  const hasActiveFilters = () => {
    return pageFilter == 'page' || tagTypeFilter.length > 0 || searchTerm;
  };

  const sortOrder = (tags: any[], pageFilter: string) => {
    if (pageFilter === 'page') {
      return orderBy(tags, ['page', 'text', 'type'], ['asc', 'asc', 'asc']);
    } else if (pageFilter === 'doc') {
      return orderBy(tags, ['text', 'type', 'page'], ['asc', 'asc', 'asc']);
    } else {
      // same for now...
      return orderBy(tags, ['text', 'type', 'page'], ['asc', 'asc', 'asc']);
    }
  };

  useEffect(() => {
    let _tags = tags;

    if (hasActiveFilters()) {
      _tags = applyFilters();
    }

    _tags = sortOrder(_tags, pageFilter);
    setFilteredList(_tags);
  }, [searchTerm, tagTypeFilter, pageFilter, tags, currentPage]);

  const applyFilter = (tag: TherapyTag | IndicationTag) => {
    const validPage = pageFilter == 'doc' ? true : currentPage == tag.page;
    console.debug(currentPage == tag.page, 'currentPage', currentPage, 'tag.page', tag.page);
    return tagTypeFilter.includes(tag._type) && validPage;
  };

  const textFilter = (tag: any, field: string, searchRegex: RegExp) => {
    return tag[field] ? `${tag[field]}`.match(searchRegex) : true;
  };

  const applyFilters = () => {
    const regex = new RegExp(searchTerm, 'i');
    return tags.filter(
      (tag: any) =>
        (textFilter(tag, 'text', regex) ||
          textFilter(tag, 'code', regex) ||
          textFilter(tag, 'name', regex)) &&
        applyFilter(tag)
    );
  };

  const onSearch = (e: any) => {
    const search = e.target.value;
    setSearchTerm(search);
  };

  //  virtual list
  const parentRef = useRef() as React.MutableRefObject<HTMLDivElement>;
  const rowVirtualizer = useVirtualizer({
    count: filteredList.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 72,
    overscan: 10,
  });

  return (
    <>
      <div className="flex flex-col bg-white">
        <div className="flex flex-1 items-center">
          <Input.Search allowClear={true} placeholder="Search" onChange={debounce(onSearch, 250)} />
        </div>
        <div className="py-2 flex flex-1 space-x-2 items-center justify-between">
          <Radio.Group
            value={pageFilter}
            onChange={(e: any) => {
              setPageFilter(e.target.value);
            }}
            optionType="button"
            options={[
              { label: 'Page Tags', value: 'page' },
              { label: 'Doc Tags', value: 'doc' },
            ]}
          />
          <Checkbox.Group
            options={[
              { label: 'Indication', value: 'indication' },
              { label: 'Therapy', value: 'therapy' },
              { label: 'Therapy Group', value: 'therapy-group' },
            ]}
            value={tagTypeFilter}
            onChange={(values: any) => {
              setTagTypeFilter(values);
            }}
          />
        </div>
      </div>

      <div className="flex flex-col p-2 pr-4 overflow-auto h-[calc(100%_-_136px)]" ref={parentRef}>
        <div
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
            position: 'relative',
          }}
        >
          {rowVirtualizer.getVirtualItems().map((virtualRow) => {
            const tag = filteredList[virtualRow.index];
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
                key={virtualRow.index}
                ref={virtualRow.measureElement}
              >
                <div className="flex">
                  <div className="flex flex-1 font-bold">{tag.name}</div>
                </div>
                <div className="flex">
                  <div className="flex items-center flex-1">{tag.text}</div>
                  <div className="flex items-center px-2">{tag.page + 1}</div>
                  <div className="flex items-center w-32 justify-center">
                    <Tag
                      color={labelColorMap(tag._type)}
                      className="capitalize select-none cursor-default"
                    >
                      {tag._type}
                    </Tag>
                  </div>
                  <div className="flex justify-center space-x-2">
                    <Button
                      onClick={() => {
                        onEditTag(tag);
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
          })}
        </div>
      </div>

      <div className="flex flex-col bg-white">
        <div className="flex flex-1 pt-4 items-center justify-between">
          <div>
            Showing {filteredList.length} of {tags.length} Tags
          </div>
          <Button onClick={(e) => {}}>Add Tag</Button>
        </div>
      </div>
    </>
  );
}
