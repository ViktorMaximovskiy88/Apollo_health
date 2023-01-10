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

export const FieldGroupsOptions = [
  { id: 'AUTHORIZATION_DETAILS', label: 'Authorization Details', value: 'AUTHORIZATION_DETAILS' },
  { id: 'TIER', label: 'Tier', value: 'TIER' },
  { id: 'COVERAGE', label: 'Medical Coverage', value: 'COVERAGE' },
  { id: 'QL_GATE', label: 'QL Gate', value: 'QL_GATE' },
  { id: 'QL_DETAILS', label: 'QL Details', value: 'QL_DETAILS' },
  { id: 'PA', label: 'PA', value: 'PA' },
  { id: 'ST', label: 'ST', value: 'ST' },
  { id: 'SP_GATE', label: 'SP Gate', value: 'SP_GATE' },
  { id: 'SP_DETAILS', label: 'SP Details', value: 'SP_DETAILS' },
  {
    id: 'TREATMENT_REQUEST_FORM',
    label: 'Treatment Request Form',
    value: 'TREATMENT_REQUEST_FORM',
  },
  { id: 'COVERAGE_NOTES', label: 'Coverage Notes', value: 'COVERAGE_NOTES' },
  { id: 'SITE_OF_CARE', label: 'Site of Care', value: 'SITE_OF_CARE' },
];

export const getFieldGroupLabel = (id: string) => {
  return FieldGroupsOptions.find((e) => {
    return e.id === id;
  })?.label;
};
