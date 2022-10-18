import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LabelList,
} from 'recharts';

import { CollectionStats } from './types';

interface PropTypes {
  collectionStats: CollectionStats[];
}

const TooltipItem = ({ item }: { item: any }) => {
  return (
    <div className="m-2 flex space-x-2">
      <div style={{ width: 40, height: 20, backgroundColor: item.fill }}></div>
      <div className="capitalize">{item.name}</div>
      <div className="flex flex-1 text-end">{item.value}</div>
    </div>
  );
};

const CustomTooltip = (args: any) => {
  const { active, payload, label } = args;
  if (active && payload && payload.length) {
    const total = payload.reduce((sum: number, item: any) => {
      return sum + item.value;
    }, 0);
    return (
      <div className="bg-white border border-solid border-gray-100 p-4">
        <div className="font-bold text-center">{label}</div>
        <TooltipItem
          item={{
            name: 'total',
            value: total,
            fill: 'white',
          }}
        />
        {payload.map((item: any, index: number) => (
          <TooltipItem key={index} item={item} />
        ))}
      </div>
    );
  }

  return null;
};

export function CollectionChart({ collectionStats }: PropTypes) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        width={500}
        height={300}
        data={collectionStats}
        margin={{
          top: 20,
          right: 30,
          left: 20,
          bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Bar dataKey="created" stackId="a" fill="#1A365D" />
        <Bar dataKey="updated" stackId="a" fill="#ECC94B">
          <LabelList
            position="top"
            valueAccessor={(item: CollectionStats) => item.created + item.updated}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
