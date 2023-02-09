import { isEqual, curry } from 'lodash';
import { Dispatch, SetStateAction, useEffect, useState } from 'react';

import { useGetDocDocumentQuery } from './docDocumentApi';
import { DocumentTag, UIIndicationTag, UITherapyTag } from './types';

const useOnPageLoadPopulateTags = ({
  setTags,
  docId,
}: {
  setTags: (tags: DocumentTag[]) => void;
  docId: string;
}) => {
  const { data: doc } = useGetDocDocumentQuery(docId);

  useEffect(() => {
    if (!doc) return;

    const therapyTags: UITherapyTag[] = doc.therapy_tags.map((tag, i) => ({
      ...tag,
      id: `${i}-therapy`,
      _type: 'therapy',
      _normalized: `${tag.name.toLowerCase()}|${tag.text.toLowerCase()}`,
    }));
    const indicationTags: UIIndicationTag[] = doc.indication_tags.map((tag, i) => ({
      ...tag,
      id: `${i}-indication`,
      _type: 'indication',
      _normalized: tag.text.toLowerCase(),
    }));
    setTags([...therapyTags, ...indicationTags]);
  }, [doc, setTags]);
};

const handleTagEdit_ = (
  {
    tags,
    setTags,
    setHasChanges,
  }: {
    tags: DocumentTag[];
    setTags: (tags: DocumentTag[]) => void;
    setHasChanges: (hasChanges: boolean) => void;
  },
  newTag: DocumentTag,
  updateTags: boolean = false
) => {
  const update = [...tags];
  const index = update.findIndex((tag) => {
    return tag.id === newTag.id;
  });
  if (index > -1) {
    if (updateTags) {
      update.forEach((tag) => {
        if (tag.id !== newTag.id && tag.text === newTag.text) {
          tag.focus = newTag.focus;
        }
      });
    }
    if (!isEqual(newTag, update[index])) setHasChanges(true);
    update[index] = newTag;
  }
  setTags(update);
};

export function useTagsState({
  docId,
  setHasChanges,
}: {
  docId: string;
  setHasChanges: (hasChanges: boolean) => void;
}): {
  tags: DocumentTag[];
  setTags: Dispatch<SetStateAction<DocumentTag[]>>;
  handleTagEdit: (newTag: DocumentTag, updateTags: boolean) => void;
} {
  const [tags, setTags] = useState<DocumentTag[]>([]);

  useOnPageLoadPopulateTags({ setTags, docId });

  const handleTagEdit = curry(handleTagEdit_)({ tags, setTags, setHasChanges });

  return { tags, setTags, handleTagEdit };
}
