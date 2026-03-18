#!/usr/bin/env npx tsx
import { acquireTokenWithDeviceCode } from './m365-auth.js';

const token = await acquireTokenWithDeviceCode();
if (token) {
  console.log('✓ Authentication successful');
} else {
  console.error('✗ Authentication failed');
  process.exit(1);
}
