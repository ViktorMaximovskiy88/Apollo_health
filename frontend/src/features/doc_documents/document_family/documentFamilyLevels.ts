export const LegacyRelevanceOptions = [
  { id: 'EDITOR_MANUAL', label: 'Editor Manual', value: 'EDITOR_MANUAL' },
  { id: 'EDITOR_AUTOMATED', label: 'Editor Automated ', value: 'EDITOR_AUTOMATED' },
  { id: 'PAR', label: 'PAR', value: 'PAR' },
  { id: 'N/A', label: 'N/A', value: 'N/A' },
];

export const getLegacyRelevanceLable = (id: string) => {
  return LegacyRelevanceOptions.find((e) => {
    return e.id === id;
  })?.label;
};
