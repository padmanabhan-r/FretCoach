# Smart Bulb Setup Guide

## Problem
The light isn't changing color when running the Electron app because the Tuya smart bulb credentials are not configured.

## Solution

### Step 1: Get Your Tuya Credentials

1. Log into the [Tuya IoT Platform](https://iot.tuya.com/)
2. Create a Cloud Project (or use an existing one)
3. Get the following credentials:
   - **Access ID** (Client ID)
   - **Access Secret** (Client Secret)
   - **Device ID** of your smart bulb
   - **Region** (e.g., "in" for India, "us" for United States, "eu" for Europe)

### Step 2: Create .env File

1. Copy the `.env.example` file to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and fill in your actual credentials:
   ```
   HAVELLS_ACCESS_ID=your_actual_access_id
   HAVELLS_ACCESS_SECRET=your_actual_access_secret
   HAVELLS_DEVICE_ID=your_actual_device_id
   HAVELLS_REGION=in
   ```

### Step 3: Restart the Electron App

1. Close the Electron app completely
2. Restart it - the app will now load the environment variables
3. The console should show: `✅ Smart bulb initialized successfully`

## Verification

When you start a practice session, you should see:
- Console message: `💡 Smart bulb enabled`
- The physical smart bulb should turn on
- As you play, the bulb color should change from red (poor) to green (good)

## Troubleshooting

### "Smart bulb credentials not configured"
- Make sure the `.env` file is in the project root directory (not in `application/` or `backend/`)
- Check that all four environment variables are set correctly
- Restart the Electron app after creating/editing the `.env` file

### "Failed to turn bulb on" or "Failed to set bulb color"
- Verify your credentials are correct in the Tuya IoT Platform
- Ensure the device is online and connected to Wi-Fi
- Check that the device ID matches your actual bulb
- Verify the region setting matches your Tuya account region

### No console messages about smart bulb
- The Electron app may not be passing environment variables
- Check that you're running the latest version of [main.js](application/electron/main.js)
- Check the Electron console for any error messages
