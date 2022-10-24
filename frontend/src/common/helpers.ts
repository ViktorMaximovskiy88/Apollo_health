/*
 * Type predicate to narrow an unknown error to an object with status and data properties
 */
export function isErrorWithData(
  error: unknown
): error is { data: { detail: string }; status: number } {
  return (
    typeof error === 'object' &&
    error != null &&
    'data' in error &&
    typeof (error as any).data === 'object' &&
    typeof (error as any).data.detail === 'string' &&
    'status' in error &&
    typeof (error as any).status === 'number'
  );
}

export function makeActionDispatch(actions: object, dispatch: any) {
  const dispatchFunctions: { [key: string]: any } = {};
  for (const [name, func] of Object.entries(actions)) {
    dispatchFunctions[name] = (...args: any[]) => dispatch(func(...args));
  }
  return dispatchFunctions;
}
