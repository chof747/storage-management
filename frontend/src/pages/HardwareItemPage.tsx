import { useEffect, useState } from 'react';
import {
  Button,
  Drawer,
  Typography,
  Box,
  AppBar,
  Toolbar
} from '@mui/material';
import {
  getItems,
  createItem,
  updateItem,
  deleteItem
} from '../api/hardwareItem';
import { HardwareItem } from '../types/hardwareItems';
import HardwareItemForm from '../components/HardwareItem/HardwareItemForm';
import HardwareItemTable from '../components/HardwareItem/HardwareItemTable';

export default function HardwareItemPage() {
  const [items, setItems] = useState<HardwareItem[]>([]);
  const [selected, setSelected] = useState<HardwareItem | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const fetchData = async () => {
    const data = await getItems();
    setItems(data);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSuccess = async () => {
    setDrawerOpen(false);
    setSelected(null);
    fetchData();
  };

  const handleSubmit = async (item: HardwareItem) => {
    if (selected?.id) {
      await updateItem({ ...item, id: selected.id });
    } else {
      await createItem(item);
    }
  };


  const handleEdit = (item: HardwareItem) => {
    setSelected(item);
    setDrawerOpen(true);
  };

  const handleCreate = () => {
    setSelected(null);
    setDrawerOpen(true);
  };

  return (
    <>
      <AppBar position="static" sx={{ mb: 2 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Hardware Inventory
          </Typography>
          <Button color="inherit" onClick={handleCreate}>
            Add Item
          </Button>
        </Toolbar>
      </AppBar>

      <Box px={2}>
        <HardwareItemTable
          items={items}
          onEdit={handleEdit}
          onDelete={async (id) => {
            await deleteItem(id);
            fetchData();
          }}
        />
      </Box>

      <Drawer anchor="right" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box width={400} p={2}>
          <Typography variant="h6" gutterBottom>
            {selected ? 'Edit Item' : 'Add New Item'}
          </Typography>
          <HardwareItemForm item={selected} onSubmit={handleSubmit} onSuccess={handleSuccess} />
        </Box>
      </Drawer>
    </>
  );
}
