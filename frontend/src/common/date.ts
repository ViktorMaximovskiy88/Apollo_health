import { DateTime, Duration } from 'luxon';

/**
 * Pretty renders a date in the specified format
 * If not render a default missing placeholder value.
 * @param value 
 * @param dateFormat 
 * @returns 
 */
export function prettyFromISO(
  value?: string,
  dateFormat = DateTime.DATETIME_FULL_WITH_SECONDS
): string {
  return value
    ? DateTime.fromISO(value, { zone: 'utc' }).toLocaleString(dateFormat)
    : '';
}

/**
 * Short date format
 * @param value 
 * @param dateFormat 
 * @returns 
 */
export function prettyDateFromISO(
  value?: string,
  dateFormat = DateTime.DATE_MED
): string {
  return prettyFromISO(value, dateFormat);
}

/**
 * Short datetime format
 * @param value 
 * @param dateFormat 
 * @returns 
 */
export function prettyDateTimeFromISO(
  value?: string,
  dateFormat = DateTime.DATETIME_MED
): string {
  return prettyFromISO(value, dateFormat);
}

/**
 * Pretty date renders a date in the default format from a date obj
 */
export function prettyDate(
  value: Date,
  dateFormat = DateTime.DATE_MED
): string {
  return DateTime.fromJSDate(value, { zone: 'utc' }).toLocaleString(dateFormat);
}

/**
 * Pretty relative date renders a date distance from the start date until the end date.
 * If the end date is missing the start date is relative to now.
 */
export function prettyDateDistance(
  startDate: string,
  endDate?: string
): string {
  const startDateTime = DateTime.fromISO(startDate);
  const endDateTime = endDate ? DateTime.fromISO(endDate) : DateTime.now();

  // precision
  const duration = endDateTime.diff(startDateTime, [
    'hours',
    'minutes',
    'seconds',
    'milliseconds',
  ]);

  // display format
  return stripZeroUnitsFromDuration(duration, [
    'hours',
    'minutes',
    'seconds',
  ]).toHuman();
}

/**
 * Helper func to strip zero value units and only show units whitelisted
 * @param duration {Duration}
 * @param displayUnits {string[]} units that we want to display
 * @returns
 */
function stripZeroUnitsFromDuration(
  duration: Duration,
  displayUnits: string[]
): Duration {
  const nonZeroUnits: any = {};
  const displayUnitsSet = new Set(displayUnits);
  for (const [unit, value] of Object.entries(duration.toObject())) {
    if (value > 0 && displayUnitsSet.has(unit)) {
      nonZeroUnits[unit] = value;
    }
  }
  return Duration.fromObject(nonZeroUnits);
}
