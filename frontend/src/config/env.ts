/**
 * Environment configuration for frontend
 * Uses Vite's environment variable system
 */

interface EnvConfig {
  apiUrl: string;
  isDevelopment: boolean;
  isProduction: boolean;
}

function getEnvConfig(): EnvConfig {
  const apiUrl = import.meta.env.VITE_API_URL || '';
  const mode = import.meta.env.MODE;

  return {
    // In development, use relative URLs (Vite proxy handles it)
    // In production, use the full backend URL
    apiUrl: mode === 'development' ? '' : apiUrl,
    isDevelopment: mode === 'development',
    isProduction: mode === 'production',
  };
}

export const env = getEnvConfig();
