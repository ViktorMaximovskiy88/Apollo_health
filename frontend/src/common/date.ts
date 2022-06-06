import {
  format,
  formatDistance,
  formatDistanceToNow,
  parseISO,
} from 'date-fns';

export enum DateFormats {
  DEFAULT_DATE_FORMAT = 'MMM d, yyyy',
  DEFAULT_MOMENT_FORMAT = 'MMM D, yyyy',
}

/**
 * Pretty date renders a date in the default format if a date is present.
 * If not render a default missing placeholder value.
 */
export function prettyDate(
  value?: string,
  dateFormat = DateFormats.DEFAULT_DATE_FORMAT
): string {
  return value ? format(parseISO(value), dateFormat) : '';
}

/**
 * Pretty relative date renders a date distance from the start date until the end date.
 * If the end date is missing the start date is relative to now.
 */
export function prettyRelativeDate(
  startDate: string,
  endDate?: string
): string {
  if (endDate) {
    return formatDistance(parseISO(startDate), parseISO(endDate));
  } else {
    return formatDistanceToNow(parseISO(startDate));
  }
}