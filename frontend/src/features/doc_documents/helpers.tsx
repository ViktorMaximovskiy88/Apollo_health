import { dateToMoment } from '../../common';
import { compact, maxBy, minBy } from 'lodash';
import { DocDocumentLocation } from './locations/types';

export const calculateFinalEffectiveFromValues = (values: any) => {
  const computeFromFields = compact([
    dateToMoment(values.effective_date),
    dateToMoment(values.last_reviewed_date),
    dateToMoment(values.last_updated_date),
  ]);

  const finalEffectiveDate: moment.Moment =
    computeFromFields.length > 0
      ? maxBy(computeFromFields, (date) => date.unix())
      : values.locations
      ? minBy(
          values.locations.map((loc: DocDocumentLocation) =>
            dateToMoment(loc.first_collected_date)
          ),
          (date) => date.unix()
        )
      : values.first_collected_date;
  return finalEffectiveDate.startOf('day');
};
