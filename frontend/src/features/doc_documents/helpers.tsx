import { dateToMoment } from '../../common';
import { compact, maxBy } from 'lodash';

export const calculateFinalEffectiveFromValues = (values: any) => {
  const computeFromFields = compact([
    dateToMoment(values.effective_date),
    dateToMoment(values.last_reviewed_date),
    dateToMoment(values.last_updated_date),
  ]);

  const finalEffectiveDate: moment.Moment =
    computeFromFields.length > 0
      ? maxBy(computeFromFields, (date) => date.unix())
      : values.first_collected_date;
  return finalEffectiveDate?.startOf('day');
};
