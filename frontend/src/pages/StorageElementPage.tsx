// HardwareItemPage.tsx
import ConfiguredEntityPage from '../components/common/ConfiguredEntityPage';
import { storageElementConfig } from './configurations/storageelement';
import { StorageElement } from '../types/storageElements';


export default function StorageElementPage() {
  return <ConfiguredEntityPage<StorageElement> config={storageElementConfig} />;
}
