import { Capacitor } from "@capacitor/core";

const API_BASE_STORAGE_KEY = "prometheus.apiBaseUrl";
const EDITOR_SETTINGS_STORAGE_KEY = "prometheus.editorSettings";
const DEFAULT_EDITOR_SETTINGS = Object.freeze({
  fontSize: 13,
  wordWrap: "on",
  minimap: false,
});

function hasWindow() {
  return typeof window !== "undefined";
}

function getStorage() {
  if (!hasWindow()) return null;
  try {
    return window.localStorage;
  } catch (_) {
    return null;
  }
}

export function normalizeApiBaseUrl(value = "") {
  return value.trim().replace(/\/+$/, "");
}

export function isNativeShell() {
  return Capacitor.isNativePlatform();
}

export function getStoredApiBaseUrl() {
  const storage = getStorage();
  if (!storage) return "";
  return normalizeApiBaseUrl(storage.getItem(API_BASE_STORAGE_KEY) || "");
}

export function setStoredApiBaseUrl(value) {
  const storage = getStorage();
  const normalized = normalizeApiBaseUrl(value || "");
  if (!storage) return normalized;
  if (normalized) {
    storage.setItem(API_BASE_STORAGE_KEY, normalized);
  } else {
    storage.removeItem(API_BASE_STORAGE_KEY);
  }
  return normalized;
}

export function getApiBaseUrl() {
  const stored = getStoredApiBaseUrl();
  if (stored) return stored;
  return normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL || "");
}

export function needsBackendConfiguration() {
  return isNativeShell() && !getApiBaseUrl();
}

export function getApiPath(path) {
  const base = getApiBaseUrl();
  return base ? `${base}${path}` : path;
}

export function getWsUrl(path) {
  const base = getApiBaseUrl();
  if (base) {
    const normalizedBase = base.endsWith("/") ? base : `${base}/`;
    const url = new URL(path, normalizedBase);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    return url.toString();
  }
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}${path}`;
}

export function getEditorSettings() {
  const storage = getStorage();
  if (!storage) return { ...DEFAULT_EDITOR_SETTINGS };
  try {
    const parsed = JSON.parse(storage.getItem(EDITOR_SETTINGS_STORAGE_KEY) || "{}");
    return { ...DEFAULT_EDITOR_SETTINGS, ...parsed };
  } catch (_) {
    return { ...DEFAULT_EDITOR_SETTINGS };
  }
}

export function setPersistedEditorSettings(settings) {
  const merged = { ...DEFAULT_EDITOR_SETTINGS, ...settings };
  const storage = getStorage();
  if (storage) {
    storage.setItem(EDITOR_SETTINGS_STORAGE_KEY, JSON.stringify(merged));
  }
  return merged;
}
