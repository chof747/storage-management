import {
  Box,
  Button,
  Collapse,
  IconButton,
  Paper,
  TextField,
  Typography,
} from '@mui/material';
import {
  FilterList as FilterListIcon,
  ExpandLess,
  ExpandMore,
} from '@mui/icons-material';
import { useState } from 'react';
import { QueryFilter } from '../../types/page';

type FilterConfig = {
  key: string;
  label: string;
  type?: 'text'; // could be extended later (e.g. dropdown, number)
};

type Props = {
  onChange: (filters: QueryFilter[]) => void;
  config: FilterConfig[];
};

export default function FilterPanel({ onChange, config }: Props) {
  const [open, setOpen] = useState(false);
  const [values, setValues] = useState<Record<string, string>>({});

  const handleFieldChange = (key: string, value: string) => {
    setValues((prev) => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    const filters: QueryFilter[] = [];
    for (const key in values) {
      if (values[key]) {
        filters.push({ key, value: values[key] });
      }
    }
    onChange(filters);
  }

  var filterFields = config.map((field) => (
    <TextField
      key={field.key}
      label={field.label}
      size="small"
      variant="outlined"
      sx={{ fontSize: '0.8rem', width: 200 }}
      InputProps={{ sx: { fontSize: '0.8rem' } }}
      InputLabelProps={{ sx: { fontSize: '0.75rem' } }}
      value={values[field.key] ?? ""}
      onChange={(e) => handleFieldChange(field.key, e.target.value)}
    />
  ))

  return (
    <>
      <Box display="flex" alignItems="center" mb={1}>
        <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
          Filters
        </Typography>
        <IconButton onClick={() => setOpen(!open)} size="small">
          {open ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}
        </IconButton>
        <IconButton onClick={() => setOpen(!open)} size="small">
          <FilterListIcon fontSize="small" />
        </IconButton>
      </Box>

      <Collapse in={open}>
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box display="flex" gap={2} flexWrap="wrap">
            {
              filterFields
            }
            <Button variant="outlined" onClick={applyFilters}>
              Apply</Button>
          </Box>
        </Paper>
      </Collapse >
    </>
  );
}
