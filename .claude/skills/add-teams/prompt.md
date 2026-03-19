# Add Microsoft Teams Channel

Adds Teams as a messaging channel to NanoClaw. Polls Teams chats (DMs and group/channel conversations) via Microsoft Graph API.

## Prerequisites

- Microsoft 365 account
- Azure AD app registration with delegated permissions

## Setup Steps

### 1. Check Dependencies

```bash
npm ls @azure/msal-node @microsoft/microsoft-graph-client 2>/dev/null || npm install @azure/msal-node @microsoft/microsoft-graph-client
```

### 2. Azure AD App Registration

AskUserQuestion: Do you already have an Azure AD app registration for NanoClaw?

**If no**, guide the user through creating one:

1. Go to https://portal.azure.com → Azure Active Directory → App registrations → New registration
2. Name: `NanoClaw` (or whatever they prefer)
3. Supported account types: "Accounts in this organizational directory only"
4. Redirect URI: leave blank (we use device code flow)
5. After creation, note the **Application (client) ID** and **Directory (tenant) ID**
6. Go to Certificates & secrets → New client secret → note the **Value**
7. Go to API permissions → Add a permission → Microsoft Graph → Delegated permissions:
   - `Chat.ReadWrite`
   - `ChannelMessage.Read.All`
   - `ChannelMessage.Send`
   - `User.Read`
8. Click "Grant admin consent" (requires admin)

AskUserQuestion: Please provide your Azure AD credentials:
- Tenant ID
- Client ID
- Client Secret (optional — not needed for device code flow, but may be required by your org)

### 3. Write Credentials to .env

Add to `.env`:
```
M365_TENANT_ID=<tenant-id>
M365_CLIENT_ID=<client-id>
```

### 4. Authenticate via Device Code

Run the device code flow to get initial tokens:

```bash
npx tsx -e "
import { acquireTokenWithDeviceCode } from './src/m365-auth.js';
const token = await acquireTokenWithDeviceCode();
if (token) console.log('✓ Authentication successful');
else { console.error('✗ Authentication failed'); process.exit(1); }
"
```

The user will need to visit a URL and enter a code shown in the output.

### 5. Choose Teams Mode

AskUserQuestion: How should Teams polling work?
- **Discover all chats** — automatically poll all Teams chats you participate in
- **Registered only** — only poll chats explicitly registered as NanoClaw groups

Add to `.env`:
```
M365_TEAMS_MODE=discover   # or "registered"
M365_TEAMS_POLL_INTERVAL=15000
```

### 6. Register Main Teams Chat

AskUserQuestion: Which Teams chat should be the main channel? (This is where admin commands and notifications go)

Help the user identify the chat ID. Run:
```bash
npx tsx -e "
import { graphGet } from './src/m365-auth.js';
const result = await graphGet('/me/chats?\$top=20&\$orderby=lastUpdatedDateTime desc');
for (const chat of result.value) {
  console.log(\`\${chat.chatType}: \${chat.topic || '(no topic)'} — ID: \${chat.id}\`);
}
"
```

Register the chosen chat as the main group using the standard NanoClaw group registration.

### 7. Create Group CLAUDE.md

Create `groups/{folder}/CLAUDE.md` with default Teams agent instructions. Follow the pattern from `groups/main/CLAUDE.md` but adapt for Teams formatting (Teams supports markdown).

### 8. Build and Verify

```bash
npm run build
```

Tell the user to restart NanoClaw and send a test message in their Teams chat.

## Troubleshooting

- **"No M365 access token available"**: Token cache expired. Re-run device code auth (step 4).
- **403 Forbidden on chat messages**: Check API permissions in Azure portal. Ensure admin consent was granted.
- **Messages not appearing**: Check `M365_TEAMS_MODE` — if `registered`, the chat must be registered as a NanoClaw group.
