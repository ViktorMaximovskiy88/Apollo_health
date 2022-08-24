import { useEffect, useState, useRef, useCallback } from 'react';
import { Button, Radio, Checkbox, Input } from 'antd';
import { debounce, orderBy } from 'lodash';
import { useVirtualizer } from '@tanstack/react-virtual';
import { TherapyTag, IndicationTag } from './types';

import { EditTag, ReadTag } from './TagRow';

function sortOrder(tags: any[], pageFilter: string) {
  if (pageFilter === 'page') {
    return orderBy(tags, ['page', '_normalized', '_type']);
  } else if (pageFilter === 'doc') {
    return orderBy(tags, ['_normalized', '_type', 'page']);
  } else {
    throw Error('what type though');
  }
}

function textFilter(tag: any, field: string, searchRegex: RegExp) {
  return tag[field] ? `${tag[field]}`.match(searchRegex) : false;
}

export function DocDocumentTagForm(props: {
  tags: Array<TherapyTag | IndicationTag>;
  onDeleteTag: Function;
  onEditTag: Function;
  onAddTag: Function;
  currentPage: number;
}) {
  const { tags, onEditTag, onDeleteTag, currentPage } = props;
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredList, setFilteredList] = useState(tags);
  const [tagTypeFilter, setTagTypeFilter] = useState<
    ('indication' | 'therapy' | 'therapy-group')[]
  >(['indication', 'therapy', 'therapy-group']);
  const [editTags, setEditTags] = useState<{ [index: string]: TherapyTag | IndicationTag }>({});
  const [pageFilter, setPageFilter] = useState('page');

  const applyFilter = useCallback(
    (tag: TherapyTag | IndicationTag) => {
      const validPage = pageFilter === 'doc' ? true : currentPage === tag.page;
      console.debug(currentPage === tag.page, 'currentPage', currentPage, 'tag.page', tag.page);
      return tagTypeFilter.includes(tag._type) && validPage;
    },
    [pageFilter, currentPage, tagTypeFilter]
  );

  const applyFilters = useCallback(() => {
    const regex = new RegExp(searchTerm, 'i');
    return tags.filter(
      (tag: any) =>
        (textFilter(tag, 'text', regex) ||
          textFilter(tag, 'code', regex) ||
          textFilter(tag, 'name', regex)) &&
        applyFilter(tag)
    );
  }, [searchTerm, tags, applyFilter]);

  useEffect(() => {
    const hasActiveFilters = pageFilter === 'page' || tagTypeFilter.length > 0 || searchTerm;
    let _tags = tags;

    if (hasActiveFilters) {
      _tags = applyFilters();
    }

    _tags = sortOrder(_tags, pageFilter);
    setFilteredList(_tags);
  }, [pageFilter, tagTypeFilter, searchTerm, applyFilters, tags]);

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

  const handleToggleEdit = (
    tag: IndicationTag | TherapyTag,
    editState: boolean,
    cancel: boolean = false
  ) => {
    if (!editState && !cancel) {
      onEditTag(editTags[tag.id]);
    }
    setEditTags((prevState) => {
      const update = { ...prevState };
      if (editState === true) {
        update[tag.id] = { ...tag };
      } else {
        delete update[tag.id];
      }
      return update;
    });
  };

  const handleEditTag = (id: string, field: string, value: any) => {
    setEditTags((prevState) => {
      const update = { ...prevState };
      const target = update[id];
      if (field === 'name' || field === 'text') {
        target[field] = value;
      } else if (field === 'page' && value != null) {
        target[field] = value - 1;
      } else if (field === 'focus') {
        (target as TherapyTag)[field] = value;
      }
      return update;
    });
  };

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
            const readOnly = !editTags[tag.id];
            if (readOnly) {
              return (
                <ReadTag
                  onDeleteTag={onDeleteTag}
                  onToggleEdit={handleToggleEdit}
                  tag={tag}
                  virtualRow={virtualRow}
                />
              );
            } else {
              return (
                <EditTag
                  onDeleteTag={onDeleteTag}
                  onEditTag={handleEditTag}
                  onToggleEdit={handleToggleEdit}
                  tag={tag}
                  virtualRow={virtualRow}
                />
              );
            }
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
