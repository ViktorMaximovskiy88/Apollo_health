import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

import { CollectionStats } from './types';

interface PropTypes {
  collectionStats: CollectionStats[];
}

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
        <Tooltip />
        <Legend />
        <Bar dataKey="total" stackId="a" fill="#82ca9d" />
        <Bar dataKey="new" stackId="a" fill="#8884d8" />
      </BarChart>
    </ResponsiveContainer>
  );
}
