// HardwareItemPage.tsx
import ConfiguredEntityPage from '../components/common/ConfiguredEntityPage';
import { createHardwareItemConfig } from './configurations/hardwareitem';
import { HardwareItem } from '../types/hardwareItems';
import { useRef, useState } from 'react';
import { FilterableTableHandle } from '../components/common/FilterableTable';


export default function HardwareItemPage() {
  const hwItemsTable = useRef<FilterableTableHandle<HardwareItem>>(null!) as React.RefObject<FilterableTableHandle<HardwareItem>>;
  const [refreshToken, setRefreshToken] = useState(0);
  return <ConfiguredEntityPage<HardwareItem> config={createHardwareItemConfig(refreshToken, setRefreshToken, hwItemsTable)} tableref={hwItemsTable} />;
}