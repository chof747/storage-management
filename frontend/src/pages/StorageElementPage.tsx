// HardwareItemPage.tsx
import ConfiguredEntityPage from '../components/common/ConfiguredEntityPage';
import { storageElementConfig } from './configurations/storageelement';
import { StorageElement } from '../types/storageElements';
import { useRef } from 'react';
import { FilterableTableHandle } from '../components/common/FilterableTable';


export default function StorageElementPage() {
  const storageElementTableRef = useRef<FilterableTableHandle<StorageElement>>(null!) as React.RefObject<FilterableTableHandle<StorageElement>>;
  return <ConfiguredEntityPage<StorageElement> config={storageElementConfig} tableref={storageElementTableRef} />;
}
