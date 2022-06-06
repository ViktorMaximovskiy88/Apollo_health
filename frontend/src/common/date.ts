import {
  format,
  formatDistance,
  formatDistanceToNow,
  parse,
  parseISO,
} from 'date-fns';

const { DEFAULT_DATE_FORMAT = 'MMM d, yyyy' } = globalThis as any;

/**
 * Pretty date renders a date in the default format if a date is present.
 * If not render a default missing placeholder value.
 */
export function prettyDate(
  value?: string,
  dateFormat = DEFAULT_DATE_FORMAT
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

/**
 * Helper function for sending our dates in ISO format to the server.
 * It ignores the timepart by setting start of day.
 */
export function toIsoDateUtc(
  value: string = '',
  dateFormat = DEFAULT_DATE_FORMAT
): string {
  const date: Date = parse(value, dateFormat, 0);
  return new Date(Date.UTC(
      date.getFullYear(),
      date.getMonth(),
      date.getDate(),
  )).toISOString();
}
