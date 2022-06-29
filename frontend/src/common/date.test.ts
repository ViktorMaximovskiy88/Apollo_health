import {
  prettyFromISO,
  prettyDateFromISO,
  prettyDateTimeFromISO,
  prettyDate,
  prettyDateDistance,
} from './date';

describe('can format UTC ISO date strings', () => {
  it('full format in local timezone', () => {
    const isoDateString = '2022-06-23T16:05:39.705000';
    const fullFormat = prettyFromISO(isoDateString);
    expect(fullFormat).toBe('June 23, 2022 at 4:05:39 PM UTC');
  });

  it('date format in local timezone', () => {
    const isoDateString = '2022-06-23T00:05:39';
    const dateFormat = prettyDateFromISO(isoDateString);
    expect(dateFormat).toBe('Jun 23, 2022');
  });

  it('datetime format in local timezone', () => {
    const isoDateString = '2022-06-23T16:05:39.705000';
    const dateTimeFormat = prettyDateTimeFromISO(isoDateString);
    expect(dateTimeFormat).toBe('Jun 23, 2022, 4:05 PM');
  });
});

it('can format from a Date object', () => {
  const date = new Date(1655956700000);
  const dateFormat = prettyDate(date);
  expect(dateFormat).toBe('Jun 23, 2022');
});

describe('can format time distance', () => {
  it('doesnt show milliseconds', () => {
    const startDate = '2022-06-23T16:05:34.705000';
    const endDate = '2022-06-23T16:05:39.7050120';
    const dateDiff = prettyDateDistance(startDate, endDate);
    expect(dateDiff).toBe('5 seconds');
  });

  it('max unit we show is in hours', () => {
    const startDate = '2022-06-22T16:05:34.705000';
    const endDate = '2022-06-23T16:05:39.7050120';
    const dateDiff = prettyDateDistance(startDate, endDate);
    expect(dateDiff).toBe('24 hours, 5 seconds');
  });

  it('show all units', () => {
    const startDate = '2022-06-22T16:05:34.705000';
    const endDate = '2022-06-23T16:15:39.7050120';
    const dateDiff = prettyDateDistance(startDate, endDate);
    expect(dateDiff).toBe('24 hours, 10 minutes, 5 seconds');
  });

  it('singular unit', () => {
    const startDate = '2022-06-23T16:05:38.705000';
    const endDate = '2022-06-23T16:05:39.7050120';
    const dateDiff = prettyDateDistance(startDate, endDate);
    expect(dateDiff).toBe('1 second');
  });
});
