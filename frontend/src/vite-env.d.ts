// src/vite-env.d.ts

/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_ENDPOINT_HOST?: string;
  readonly VITE_API_ENDPOINT_PORT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
