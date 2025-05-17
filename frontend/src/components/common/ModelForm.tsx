import React, { useEffect, useState } from 'react';
import renderTextField from './formitems/textfield';
import renderNumberField from './formitems/numberfield';
import { renderCheckboxField } from './formitems/checkboxfield';
import renderSelectWithCreate from './formitems/selectWithCreate';
import {
  Box,
  Button,
  Paper,
} from '@mui/material';

export type FormField<T> = {
  name: keyof T;
  label: string;
  type?: 'text' | 'number' | 'select' | 'select-create' | 'boolean';
  required?: boolean;
  loadOptions?: () => Promise<{ id: number; label: string }[]>;
  options?: { id: number; label: string }[];
  createNew?: () => Promise<{ id: number; label: string }>;
};

export type Props<T> = {
  fields: FormField<T>[];
  initialValues?: Partial<T>;
  onValidSubmit: (data: T) => Promise<void>;
  onSuccess: () => void;
  submitLabel?: string;
};

function isErrorWithResponse(err: unknown): err is Error & { response?: Response } {
  return (
    typeof err === 'object' &&
    err !== null &&
    'message' in err &&
    typeof (err as { message?: unknown }).message === 'string' &&
    'response' in err
  );
}

function ModelForm<T extends object>({
  fields,
  initialValues = {},
  onValidSubmit,
  onSuccess,
  submitLabel = 'Submit',
}: Props<T>) {
  const [form, setForm] = useState<Partial<T>>(initialValues);
  const [selectOptions, setSelectOptions] = useState<Record<string, { id: number; label: string }[]>>({});
  const [loadingSelects, setLoadingSelects] = useState<Record<string, boolean>>({});
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    setForm(initialValues);
  }, [initialValues]);

  // Load async select options
  useEffect(() => {
    fields.forEach((field) => {
      if (field.type === 'select-create' && field.loadOptions && !selectOptions[field.name as string]) {
        setLoadingSelects((prev) => ({ ...prev, [field.name as string]: true }));
        field
          .loadOptions()
          .then((opts) => {
            setSelectOptions((prev) => ({ ...prev, [String(field.name)]: opts }));
          })
          .finally(() => {
            setLoadingSelects((prev) => ({ ...prev, [field.name as string]: false }));
          });
      }
    });
  }, [fields]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    const fieldDef = fields.find((f) => f.name === name);

    let newValue: string | number | boolean | '' = value;

    if (fieldDef?.type === 'number') {
      newValue = parseFloat(value) || '';
    } else if (fieldDef?.type === 'boolean' && e.target instanceof HTMLInputElement) {
      newValue = e.target.checked;
    } else {
      newValue = value;
    }

    setForm((prev) => ({
      ...prev,
      [name]: newValue,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);
    setFieldErrors({});

    try {
      await onValidSubmit(form as T);
      onSuccess();
    } catch (err: unknown) {
      if (isErrorWithResponse(err)) {
        if (err.name === 'ValidationError') {
          // Custom validation
        } else if (err.response?.status === 422) {
          const data = await err.response.json();
          const errors: Record<string, string> = {};
          for (const detail of data.detail) {
            const loc = detail.loc[detail.loc.length - 1];
            errors[loc] = detail.msg;
          }
          setFieldErrors(errors);
          setGeneralError("Please correct the highlighted errors.");
        } else if (err.response?.status === 400 || err.response?.status === 500) {
          const data = await err.response.json();
          setGeneralError(data.detail || "Something went wrong.");
        } else {
          setGeneralError("Unknown error occurred.");
        }
      }
    }
  };

  const renderField = (field: FormField<T>) => {
    const name = String(field.name);
    const value = form[field.name] ?? '';
    const error = fieldErrors[name];
    const loading = loadingSelects[name] || false;
    const options = field.options ?? selectOptions[name] ?? [];

    switch (field.type) {
      //      case 'select':
      //        return renderSelectField(field, value, error, handleChange, loading, options);
      case 'select-create':
        return renderSelectWithCreate(
          field,
          (typeof (value) == 'number') ? value : "",
          error,
          handleChange,
          loading,
          options,
          (id, label) => {
            setSelectOptions((prev) => {
              const key = String(field.name);
              const existing = prev[key] || [];
              return {
                ...prev,
                [key]: [...existing, { id, label }]
              };
            });
            setForm((prev) => ({ ...prev, [field.name]: id }));
          }
        );
      case 'boolean':
        return renderCheckboxField(field, Boolean(value), handleChange);
      case 'number':
        return renderNumberField(field, (typeof (value) == 'number') ? value : 0, error, handleChange);
      case 'text':
      default:
        return renderTextField(field, (typeof (value) == 'string') ? value : '', error, handleChange);
    };
  };

  return (
    <Paper sx={{ p: 2 }}>
      {generalError && (
        <Box
          sx={{
            backgroundColor: '#fdecea',
            border: '1px solid #f5c2c0',
            color: '#a94442',
            fontSize: '0.875rem',
            p: 1,
            mb: 2,
            borderRadius: 1,
          }}
        >
          {generalError}
        </Box>
      )}
      <form onSubmit={handleSubmit}>
        <Box display="flex" flexDirection="column" gap={2}>
          {fields.map(renderField)}
          <Box>
            <Button variant="contained" type="submit">
              {submitLabel}
            </Button>
          </Box>
        </Box>
      </form>
    </Paper>
  );
}

export default ModelForm;
