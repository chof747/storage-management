import EntityPage from '../components/common/EntityPage';
import { getItems, createItem, updateItem, deleteItem } from '../api/hardwareItem';
import { HardwareItem } from '../types/hardwareItems';
import HardwareItemForm from '../components/HardwareItem/HardwareItemForm';
import HardwareItemTable from '../components/HardwareItem/HardwareItemTable';

export default function HardwareItemPage() {
  return (
    <EntityPage<HardwareItem>
      title="Hardware Inventory"
      fetchItems={getItems}
      createItem={createItem}
      updateItem={updateItem}
      deleteItem={deleteItem}
      FormComponent={HardwareItemForm}
      TableComponent={HardwareItemTable}
      getItemId={(item) => item.id!}
    />
  );
}
