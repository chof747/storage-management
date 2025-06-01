export interface AppConfig {
  API_ENDPOINT_HOST: string;
  API_ENDPOINT_PORT: number;
}

let config: AppConfig | null = null;

export async function loadConfig(): Promise<AppConfig> {
  if (config) {
    // already loaded
    return config;
  }

  const response = await fetch('/config.json');
  if (!response.ok) {
    throw new Error('Failed to load config.json');
  }

  config = await response.json();
  if (config) {
    return config;
  }
  else {
    return {
      API_ENDPOINT_HOST: "localhost",
      API_ENDPOINT_PORT: 8000
    }
  }
}
