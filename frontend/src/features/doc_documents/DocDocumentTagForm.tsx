import { useEffect, useState, useRef } from 'react';
import { Button, Radio, Tag, Checkbox, Input } from 'antd';
import { DeleteOutlined, EditOutlined } from '@ant-design/icons';
import debounce from 'lodash.debounce';
import { useVirtualizer } from '@tanstack/react-virtual';
import { BaseDocTag } from './types';

export function DocDocumentTagForm(props: {
  tags: BaseDocTag[];
  onDeleteTag: Function;
  onEditTag: Function;
  onAddTag: Function;
}) {
  const { tags, onEditTag, onAddTag, onDeleteTag } = props;
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredList, setFilteredList] = useState(tags);
  const [tagTypeFilter, setTagTypeFilter] = useState(['indication', 'therapy', 'therapy-group']);
  const [pageFilter, setPageFilter] = useState('doc');

  const hasActiveFilters = () => {
    return pageFilter == 'page' || tagTypeFilter.length > 0 || searchTerm;
  };

  useEffect(() => {
    if (hasActiveFilters()) {
      applyFilters();
    } else {
      setFilteredList(tags);
    }
  }, [searchTerm, tagTypeFilter, pageFilter, tags]);

  const applyFilter = (tag: any) => {
    const currentPage = 0;
    const validPage = pageFilter == 'doc' ? true : currentPage == tag.page;
    return tagTypeFilter.includes(tag.type) && validPage;
  };

  const applyFilters = () => {
    const regex = new RegExp(searchTerm, 'i');
    const filteredTags = tags.filter(
      (tag: any) => (tag.text.match(regex) || tag.code.match(regex)) && applyFilter(tag)
    );
    setFilteredList(filteredTags);
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
    estimateSize: () => 55.5,
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
              console.log(e);
              setPageFilter(e.target.value);
            }}
            optionType="button"
            options={[
              { label: 'Doc Tags', value: 'doc' },
              { label: 'Page Tags', value: 'page' },
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
          {rowVirtualizer.getVirtualItems().map((virtualItem) => {
            const tag = filteredList[virtualItem.index];
            return (
              <div
                className="flex flex-row py-4"
                style={{
                  borderTop: '1px solid #ccc',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: `${virtualItem.size}px`,
                  transform: `translateY(${virtualItem.start}px)`,
                }}
                key={virtualItem.index}
              >
                <div className="flex flex-1">{tag.text}</div>
                <div className="">
                  <Tag className="capitalize select-none cursor-default">{tag.type}</Tag>
                </div>
                <div className="flex">
                  <EditOutlined
                    className="cursor-pointer p-2 flex items-center"
                    onClick={() => {
                      onEditTag(tag);
                    }}
                  />

                  <DeleteOutlined
                    className="cursor-pointer p-2 flex items-center"
                    onClick={() => {
                      onDeleteTag(tag);
                    }}
                  />
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
          <Button
            onClick={(e) => {
              onAddTag({
                text: `Tag ${+new Date()}`,
                code: `${+new Date()}`,
                score: -1,
                type: 'indication',
                relevancy: 1,
                page: 1,
              });
            }}
          >
            Add Tag
          </Button>
        </div>
      </div>
    </>
  );
}
