import { Route, Routes } from 'react-router-dom';
import { CollectionStatsPage } from './CollectionStatsPage';

export function StatsRoutes() {
  return (
    <Routes>
      <Route path="/collection" element={<CollectionStatsPage />} />
    </Routes>
  );
}
