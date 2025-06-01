import { useState } from 'react';
import {
  AppBar,
  Box,
  Button,
  Drawer,
  Toolbar,
  Typography,
} from '@mui/material';
import { ResultPage } from '../../types/page';
import { FilterableTableHandle } from './FilterableTable';

type EntityPageProps<T> = {
  title: string;
  toolbar: boolean;
  fetchItems: (offset: number, limit: number) => Promise<ResultPage<T>>;
  createItem: (item: T) => Promise<T>;
  updateItem: (item: T) => Promise<T>;
  deleteItem: (id: number) => Promise<void>;
  FormComponent: React.ComponentType<{
    item: T | null;
    onSubmit: (item: T) => Promise<void>;
    onSuccess: (doAnother: boolean) => void;
  }>;
  TableComponent: React.ComponentType<{
    fetchItems: (offset: number, limit: number) => Promise<ResultPage<T>>;
    onEdit: (item: T) => void;
    onDelete: (id: number) => void;
  }>;
  getItemId: (item: T) => number;
  tableRef?: React.RefObject<FilterableTableHandle<T>>;


};

export default function EntityPage<T>({
  title,
  toolbar,
  fetchItems,
  createItem,
  updateItem,
  deleteItem,
  FormComponent,
  TableComponent,
  tableRef,
}: EntityPageProps<T>) {
  const [selected, setSelected] = useState<T | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleSubmit = async (item: T) => {
    if (selected) {
      await updateItem(item);
    } else {
      await createItem(item);
    }
  };

  const handleDelete = async (id: number) => {
    await deleteItem(id);
    tableRef?.current?.refresh();
  };

  const handleSuccess = (doAnother: boolean) => {
    setDrawerOpen(doAnother);
    setSelected(null);
    tableRef?.current?.refresh();
  };

  const addButton = () => <Button color="inherit" onClick={() => {
    setSelected(null);
    setDrawerOpen(true);
  }}>
    Add Item
  </Button>;

  return (
    <>

      {
        toolbar ?
          <>
            <AppBar position="static" sx={{ mb: 2 }}>
              <Toolbar>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                  {title}
                </Typography>
                {addButton()}
              </Toolbar>
            </AppBar></>
          :
          ""
      }

      <Box>
        <TableComponent
          fetchItems={fetchItems}
          onEdit={(item) => {
            setSelected(item);
            setDrawerOpen(true);
          }}
          onDelete={(id) => handleDelete(id)}
        />

        {
          !toolbar ?
            <>{addButton()}</>
            : ""
        }
      </Box>

      <Drawer anchor="right" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box width={400} p={2} pt={9}>
          <Typography variant="h6" gutterBottom>
            {selected ? 'Edit Item' : 'Add New Item'}
          </Typography>
          <FormComponent
            item={selected}
            onSubmit={handleSubmit}
            onSuccess={handleSuccess}
          />
        </Box>
      </Drawer>
    </>
  );
}
