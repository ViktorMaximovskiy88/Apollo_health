import { useEffect, useState, useRef } from 'react';
import { Button, Radio, Tag, Checkbox, Input } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import debounce from 'lodash.debounce';
import { useVirtualizer } from '@tanstack/react-virtual';

import { DocDocument } from './types';
import { BaseDocTag } from './types';

export function DocDocumentTagForm(props: { doc: DocDocument; form: any }) {
  const { doc } = props;

  const allTags: BaseDocTag[] = [...doc.therapy_tags, ...doc.indication_tags];

  const tags = [
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
  ];

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
  }, [searchTerm, tagTypeFilter, pageFilter]);

  const applyFilter = (tag: any) => {
    const currentPage = 0;
    const validPage = pageFilter == 'doc' ? true : currentPage == tag.page;
    return tagTypeFilter.includes(tag.type) && validPage;
  };

  const applyFilters = () => {
    const regex = new RegExp(searchTerm, 'i');
    const filteredTags = tags.filter((tag: any) => {
      return (tag.text.match(regex) || tag.code.match(regex)) && applyFilter(tag);
    });
    setFilteredList(filteredTags);
  };

  const onSearch = (e: any) => {
    const search = e.target.value;
    setSearchTerm(search);
  };

  // The scrollable element for your list
  const parentRef = useRef() as React.MutableRefObject<HTMLDivElement>;

  // The virtualizer
  const rowVirtualizer = useVirtualizer({
    count: filteredList.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 55.5,
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

      <div
        className="flex flex-col p-2 pr-4 overflow-auto flex-1 h-[calc(100%_-_136px)]"
        ref={parentRef}
      >
        <div
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
            width: '100%',
            position: 'relative',
          }}
        >
          {rowVirtualizer.getVirtualItems().map((virtualItem) => {
            const tag = filteredList[virtualItem.index];
            return (
              <div
                className="flex flex-row py-4"
                style={{ borderTop: '1px solid #ccc' }}
                key={virtualItem.index}
              >
                <div className="flex flex-1">{tag.text}</div>
                <div className="">
                  <Tag className="capitalize select-none cursor-default">{tag.type}</Tag>
                </div>
                <div className="flex">
                  <DeleteOutlined
                    className="cursor-pointer"
                    onClick={(e) => {
                      console.log(e);
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
          <Button>Add Tag</Button>
        </div>
      </div>
    </>
  );
}
