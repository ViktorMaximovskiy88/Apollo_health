export const ListViewItem = ({ label, children }: { label: string; children: any }) => {
  return (
    <div className="mt-1 mb-2">
      <div className="text-sm text-gray-700">{label}</div>
      {children}
    </div>
  );
};
