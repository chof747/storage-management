import { loadConfig, AppConfig } from '../config';

export async function getApiBase(): Promise<string> {
  const config: AppConfig = await loadConfig();
  return `http://${config.API_ENDPOINT_HOST}:${config.API_ENDPOINT_PORT}/api`;
}
