// HardwareItemPage.tsx
import ConfiguredEntityPage from '../components/common/ConfiguredEntityPage';
import { createHardwareItemConfig } from './configurations/hardwareitem';
import { HardwareItem } from '../types/hardwareItems';
import { useRef } from 'react';
import { FilterableTableHandle } from '../components/common/FilterableTable';


export default function HardwareItemPage() {
  const hwItemsTable = useRef<FilterableTableHandle<HardwareItem>>(null!) as React.RefObject<FilterableTableHandle<HardwareItem>>;
  return <ConfiguredEntityPage<HardwareItem> config={createHardwareItemConfig(hwItemsTable)} tableref={hwItemsTable} />;
}