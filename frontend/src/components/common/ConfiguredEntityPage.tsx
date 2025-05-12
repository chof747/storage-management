// ConfiguredEntityPage.tsx
import EntityPage from './EntityPage';
import FilterableTable, { FilterableTableHandle, TableColumn } from './FilterableTable';
import ModelForm, { FormField } from './ModelForm';
import React from 'react';
import { ResultPage } from '../../types/page';

export type EntityConfig<T extends Record<string, any>> = {
  title: string;
  toolbar: boolean;
  selectitems?: boolean;
  onSelectionChange?: (selectedItems: T[]) => void;
  fetchItems: (offset: number, limit: number) => Promise<ResultPage<T>>;
  createItem: (item: T) => Promise<T>;
  updateItem: (item: T) => Promise<T>;
  deleteItem: (id: number) => Promise<void>;
  getItemId: (item: T) => number;
  form: {
    fields: FormField<T>[];
  };
  table: {
    columns: TableColumn<T>[];
    customActions?: (item: T, refresh: () => void) => React.ReactNode;
  };
};

export default function ConfiguredEntityPage<T extends Record<string, any>>({
  config, tableref
}: {
  config: EntityConfig<T>;
  tableref?: React.RefObject<FilterableTableHandle<T>>;
}) {
  const TableComponent = (props: any) => (
    <FilterableTable<T>
      ref={tableref}
      fetchItems={props.fetchItems}
      columns={config.table.columns}
      onEdit={props.onEdit}
      onDelete={(item) => props.onDelete(config.getItemId(item))}
      customActions={config.table.customActions
        ? (item, _) => config.table.customActions!(item, props.onRefresh)
        : undefined}
      getRowId={config.getItemId}
      selectableRows={config.selectitems ?? false}
      onSelectionChange={config.onSelectionChange ?? undefined}
    />
  );

  const FormComponent = ({ item, onSubmit, onSuccess }: any) => (
    <ModelForm<T>
      fields={config.form.fields}
      initialValues={item ?? {}}
      onValidSubmit={onSubmit}
      onSuccess={onSuccess}
      submitLabel={item ? 'Update' : 'Add'}
    />
  );

  return (
    <EntityPage<T>
      title={config.title}
      toolbar={config.toolbar}
      fetchItems={config.fetchItems}
      createItem={config.createItem}
      updateItem={config.updateItem}
      deleteItem={config.deleteItem}
      getItemId={config.getItemId}
      FormComponent={FormComponent}
      TableComponent={TableComponent}
      tableRef={tableref}
    />
  );
}
