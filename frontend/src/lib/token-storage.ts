type Strategy = 'cookie' | 'pwa' | 'native';

declare global {
  interface Window {
    Capacitor?: {
      Plugins?: {
        SecureStoragePlugin?: {
          set(options: { key: string; value: string }): Promise<void>;
          get(options: { key: string }): Promise<{ value?: string }>;
          remove(options: { key: string }): Promise<void>;
        };
      };
    };
  }
}

const STORAGE_KEY = 'traveltailor.auth.token';

function detectStrategy(): Strategy {
  if (typeof window === 'undefined') {
    return 'cookie';
  }
  // Capacitor exposes a global object in hybrid builds
  if (window?.Capacitor) {
    return 'native';
  }
  if (window.matchMedia?.('(display-mode: standalone)').matches) {
    return 'pwa';
  }
  return 'cookie';
}

async function deriveKey(): Promise<CryptoKey> {
  if (!window.crypto?.subtle) {
    throw new Error('WebCrypto not available');
  }
  const encoder = new TextEncoder();
  const material = await window.crypto.subtle.importKey(
    'raw',
    encoder.encode(navigator.userAgent),
    'PBKDF2',
    false,
    ['deriveKey'],
  );
  return window.crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: encoder.encode(window.location.origin),
      iterations: 5000,
      hash: 'SHA-256',
    },
    material,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt'],
  );
}

function encode(buffer: ArrayBuffer): string {
  return btoa(String.fromCharCode(...new Uint8Array(buffer)));
}

function decode(value: string): Uint8Array {
  return Uint8Array.from(atob(value), (c) => c.charCodeAt(0));
}

async function encryptToken(token: string): Promise<string> {
  try {
    const key = await deriveKey();
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const cipher = await window.crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      key,
      new TextEncoder().encode(token),
    );
    return `${encode(iv)}.${encode(cipher)}`;
  } catch {
    return token;
  }
}

async function decryptToken(value: string | null): Promise<string | null> {
  if (!value) {
    return null;
  }
  const [ivEncoded, cipherEncoded] = value.split('.');
  if (!ivEncoded || !cipherEncoded) {
    return value;
  }
  try {
    const key = await deriveKey();
    const plain = await window.crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: decode(ivEncoded) },
      key,
      decode(cipherEncoded),
    );
    return new TextDecoder().decode(plain);
  } catch {
    return value;
  }
}

async function storeNative(token: string): Promise<void> {
  if (!window.Capacitor?.Plugins?.SecureStoragePlugin) {
    localStorage.setItem(STORAGE_KEY, await encryptToken(token));
    return;
  }
  await window.Capacitor.Plugins.SecureStoragePlugin.set({ key: STORAGE_KEY, value: token });
}

async function readNative(): Promise<string | null> {
  if (!window.Capacitor?.Plugins?.SecureStoragePlugin) {
    return decryptToken(localStorage.getItem(STORAGE_KEY));
  }
  try {
    const result = await window.Capacitor.Plugins.SecureStoragePlugin.get({ key: STORAGE_KEY });
    return result.value ?? null;
  } catch {
    return null;
  }
}

export async function storeToken(token: string): Promise<void> {
  const strategy = detectStrategy();
  if (strategy === 'cookie') {
    // Backend sets httpOnly cookie; nothing to do
    return;
  }
  if (strategy === 'native') {
    await storeNative(token);
    return;
  }
  const encrypted = await encryptToken(token);
  localStorage.setItem(STORAGE_KEY, encrypted);
}

export async function readToken(): Promise<string | null> {
  const strategy = detectStrategy();
  if (strategy === 'cookie') {
    return null;
  }
  if (strategy === 'native') {
    return readNative();
  }
  return decryptToken(localStorage.getItem(STORAGE_KEY));
}

export async function clearToken(): Promise<void> {
  const strategy = detectStrategy();
  if (strategy === 'cookie') {
    return;
  }
  if (strategy === 'native' && window.Capacitor?.Plugins?.SecureStoragePlugin) {
    await window.Capacitor.Plugins.SecureStoragePlugin.remove({ key: STORAGE_KEY });
  }
  localStorage.removeItem(STORAGE_KEY);
}

export { detectStrategy };
