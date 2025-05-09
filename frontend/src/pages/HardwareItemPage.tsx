// HardwareItemPage.tsx
import ConfiguredEntityPage from '../components/common/ConfiguredEntityPage';
import { createHardwareItemConfig } from './configurations/hardwareitem';
import { HardwareItem } from '../types/hardwareItems';


export default function HardwareItemPage() {
  return <ConfiguredEntityPage<HardwareItem> config={createHardwareItemConfig()} />;
}