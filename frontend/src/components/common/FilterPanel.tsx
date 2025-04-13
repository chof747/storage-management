import {
  Box,
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

type FilterConfig = {
  key: string;
  label: string;
  type?: 'text'; // could be extended later (e.g. dropdown, number)
};

type Props = {
  filters: Record<string, string>;
  onChange: (key: string, value: string) => void;
  config: FilterConfig[];
};

export default function FilterPanel({ filters, onChange, config }: Props) {
  const [open, setOpen] = useState(true);

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
            {config.map((field) => (
              <TextField
                key={field.key}
                label={field.label}
                size="small"
                variant="outlined"
                value={filters[field.key] ?? ''}
                onChange={(e) => onChange(field.key, e.target.value)}
                sx={{ fontSize: '0.8rem', width: 200 }}
                InputProps={{ sx: { fontSize: '0.8rem' } }}
                InputLabelProps={{ sx: { fontSize: '0.75rem' } }}
              />
            ))}
          </Box>
        </Paper>
      </Collapse>
    </>
  );
}
