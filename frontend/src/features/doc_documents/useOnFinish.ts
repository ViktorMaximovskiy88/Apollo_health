import { useGetDocDocumentQuery } from './docDocumentApi';
import { DocDocument, DocumentTag, IndicationTag, TherapyTag } from './types';

export const focusDocumentTypes = [
  'Exclusion List',
  'Fee Schedule',
  'Formulary',
  'Formulary Update',
  'Medical Coverage List',
  'Payer Unlisted Policy',
  'Preventive Drug List',
  'Restriction List',
  'Specialty List',
];

interface UseOnFinishType {
  onSubmit: (doc: Partial<DocDocument>) => Promise<void>;
  tags: DocumentTag[];
  setIsSaving: (isSaving: boolean) => void;
  docId: string;
}
export const useOnFinish = ({
  onSubmit,
  tags,
  setIsSaving,
  docId,
}: UseOnFinishType): ((doc: Partial<DocDocument>) => void) => {
  const { data: doc } = useGetDocDocumentQuery(docId);
  const onFinish = async (submittedDoc: Partial<DocDocument>): Promise<void> => {
    if (!submittedDoc) return;

    setIsSaving(true);

    try {
      const indication_tags: IndicationTag[] = [];
      const therapy_tags: TherapyTag[] = [];
      for (const uiTag of tags) {
        const { id, _type, _normalized, ...tag } = uiTag;
        if (_type === 'indication') {
          indication_tags.push(tag as IndicationTag);
        } else {
          therapy_tags.push(tag as TherapyTag);
        }
      }

      submittedDoc.previous_par_id = submittedDoc.previous_par_id || null;
      submittedDoc.document_family_id = submittedDoc.document_family_id || null;
      submittedDoc.locations = doc?.locations.map((loc, i) => ({
        ...loc,
        ...(submittedDoc.locations || [])[i],
      }));

      await onSubmit({
        ...submittedDoc,
        indication_tags,
        therapy_tags,
        _id: docId,
      });
    } catch (error) {
      //  TODO real errors please
      console.error(error);
    }
    setIsSaving(false);
  };

  return onFinish;
};
