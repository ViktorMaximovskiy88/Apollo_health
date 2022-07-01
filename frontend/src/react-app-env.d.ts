/// <reference types="react-scripts" />
import { Settings } from './settings';
export {};

declare global {
  interface Window {
    _settings: Settings;
  }
}
