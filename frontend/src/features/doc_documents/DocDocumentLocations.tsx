import { DocDocumentLocation } from './types';

interface DocDocumentLocationPropTypes {
  locations: DocDocumentLocation[];
}

interface PropertyGridPropTypes {
  label: string;
  value: string;
  href: string;
}

export const PropertyGridItem = ({ label, value, href }: PropertyGridPropTypes) => {
  return (
    <div className="mb-2">
      {href ? (
        <a target="_blank" href={href} rel="noreferrer">
          {value}
        </a>
      ) : (
        <span>{value}</span>
      )}
      <div className="uppercase text-gray-700 text-xs">{label}</div>
    </div>
  );
};

export const DocDocumentLocations = (props: DocDocumentLocationPropTypes) => {
  const { locations } = props;
  return (
    <div>
      {locations.map((location, index) => (
        <div key={index}>
          <PropertyGridItem label={'Base URL'} value={location.base_url} href={location.base_url} />
          <PropertyGridItem label={'URL'} value={location.url} href={location.url} />
        </div>
      ))}
    </div>
  );
};
