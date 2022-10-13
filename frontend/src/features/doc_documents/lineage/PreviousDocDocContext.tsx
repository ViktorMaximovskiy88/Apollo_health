import { createContext, Dispatch, ReactNode, SetStateAction, useState } from 'react';

export const PreviousDocDocContext = createContext<[string, Dispatch<SetStateAction<string>>]>([
  '',
  () => {},
]);

export function PreviousDocDocProvider({
  children,
  initialValue,
  ...props
}: {
  children: ReactNode;
  initialValue?: string;
}) {
  const [previousDocDocumentId, setPreviousDocDocumentId] = useState(initialValue ?? '');
  return (
    <PreviousDocDocContext.Provider
      {...props}
      value={[previousDocDocumentId, setPreviousDocDocumentId]}
    >
      {children}
    </PreviousDocDocContext.Provider>
  );
}
