import EntityPage from '../components/common/EntityPage';
import { getItems, createItem, updateItem, deleteItem } from '../api/storageElement';
import { StorageElement } from '../types/storageElements';
import StorageElementForm from '../components/StorageElement/StorageElementForm';
import StorageElementTable from '../components/StorageElement/StorageElementTable';

export default function StorageElementPage() {
  return (
    <EntityPage<StorageElement>
      title="Hardware Inventory"
      fetchItems={getItems}
      createItem={createItem}
      updateItem={updateItem}
      deleteItem={deleteItem}
      FormComponent={StorageElementForm}
      TableComponent={StorageElementTable}
      getItemId={(item) => item.id!}
    />
  );
}
