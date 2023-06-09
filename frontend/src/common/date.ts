import { DateTime, Duration } from 'luxon';
import moment from 'moment';

/**
 *
 * @param date
 * @returns
 */
export function dateToMoment(date?: string) {
  return date ? moment.utc(date) : undefined;
}

/**
 * Pretty renders a date in the specified format
 * If not render a default missing placeholder value.
 * @param value
 * @param dateFormat
 * @param toLocal
 * @returns
 */
export function prettyFromISO(
  value?: string,
  dateFormat = DateTime.DATETIME_FULL_WITH_SECONDS,
  toLocal = true
): string {
  if (value) {
    let dateTime = DateTime.fromISO(value, { zone: 'utc' });
    if (toLocal) dateTime = dateTime.toLocal();
    return dateTime.toLocaleString(dateFormat);
  } else {
    return '';
  }
}

/**
 * Short date format in UTC
 * @param value
 * @param dateFormat
 * @returns
 */
export function prettyDateUTCFromISO(value?: string, dateFormat = DateTime.DATE_MED): string {
  return prettyFromISO(value, dateFormat, false);
}

/**
 * Short date format
 * @param value
 * @param dateFormat
 * @returns
 */
export function prettyDateFromISO(value?: string, dateFormat = DateTime.DATE_MED): string {
  return prettyFromISO(value, dateFormat);
}

/**
 * Short datetime format in UTC
 * @param value
 * @param dateFormat
 * @returns
 */
export function prettyDateTimeUTCFromISO(
  value?: string,
  dateFormat = DateTime.DATETIME_MED
): string {
  return prettyFromISO(value, dateFormat, false);
}

/**
 * Short datetime format
 * @param value
 * @param dateFormat
 * @returns
 */
export function prettyDateTimeFromISO(value?: string, dateFormat = DateTime.DATETIME_MED): string {
  return prettyFromISO(value, dateFormat);
}

/**
 * Pretty date renders a date in the default format from a date obj
 */
export function prettyDate(value: Date, dateFormat = DateTime.DATE_MED): string {
  return DateTime.fromJSDate(value, { zone: 'utc' }).toLocaleString(dateFormat);
}

export function dateDuration(startDate: string, endDate?: string) {
  const startDateTime = DateTime.fromISO(startDate, { zone: 'utc' });
  const endDateTime = endDate ? DateTime.fromISO(endDate, { zone: 'utc' }) : DateTime.utc();
  const duration = endDateTime.diff(startDateTime, ['hours', 'minutes', 'seconds', 'milliseconds']);
  return duration;
}

/**
 * Pretty relative date renders a date distance from the start date until the end date.
 * If the end date is missing the start date is relative to now.
 */
export function prettyDateDistance(startDate: string, endDate?: string): string {
  // precision
  const duration = dateDuration(startDate, endDate);

  // display format
  return stripZeroUnitsFromDuration(duration, ['hours', 'minutes', 'seconds']).toHuman();
}

/**
 * Pretty relative date renders a date distance from the start date until the end date.
 * If the end date is missing the start date is relative to now.
 * Returns a single number like '4.93 minutes' or '2.1' hours
 */
export function prettyDateDistanceSingle(startDate: string, endDate?: string): string {
  // precision
  let dur = dateDuration(startDate, endDate);

  // display format
  dur = stripZeroUnitsFromDuration(dur, ['hours', 'minutes', 'seconds']);
  if (dur.hours) {
    const hours = dur.hours + (dur.minutes > 2 ? dur.minutes / 60 : 0);
    return `${hours.toPrecision(3)} hour${hours == 1 ? '' : 's'}`;
  }
  if (dur.minutes) {
    const min = dur.minutes + (dur.seconds > 2 ? dur.seconds / 60 : 0);
    return `${min.toPrecision(3)} minute${min == 1 ? '' : 's'}`;
  }
  return dur.toHuman();
}

/**
 * Helper func to strip zero value units and only show units whitelisted
 * @param duration {Duration}
 * @param displayUnits {string[]} units that we want to display
 * @returns
 */
function stripZeroUnitsFromDuration(duration: Duration, displayUnits: string[]): Duration {
  const nonZeroUnits: any = {};
  const displayUnitsSet = new Set(displayUnits);
  for (const [unit, value] of Object.entries(duration.toObject())) {
    if (value > 0 && displayUnitsSet.has(unit)) {
      nonZeroUnits[unit] = value;
    }
  }
  return Duration.fromObject(nonZeroUnits);
}
