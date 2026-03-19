#!/usr/bin/env npx tsx
/**
 * Ensures a private "MyAssistant" group chat exists in Teams.
 * Creates it if it doesn't exist, then prints the chat ID.
 */
import { graphGet, graphPost } from './m365-auth.js';

const CHAT_TOPIC = 'MyAssistant';

interface TeamsChat {
  id: string;
  chatType: string;
  topic: string | null;
}

// Check if a "MyAssistant" chat already exists
const result = await graphGet<{ value: TeamsChat[] }>(
  '/me/chats?$top=50',
);

const existing = result.value.find(
  (c) => c.topic?.toLowerCase() === CHAT_TOPIC.toLowerCase(),
);

if (existing) {
  console.log(`Found existing "${CHAT_TOPIC}" chat: ${existing.id}`);
  process.exit(0);
}

// Get the current user's ID to add as member
const me = await graphGet<{ id: string; displayName: string }>('/me');

// Create a new group chat with just the current user
const newChat = await graphPost<TeamsChat>('/chats', {
  chatType: 'group',
  topic: CHAT_TOPIC,
  members: [
    {
      '@odata.type': '#microsoft.graph.aadUserConversationMember',
      roles: ['owner'],
      'user@odata.bind': `https://graph.microsoft.com/v1.0/users('${me.id}')`,
    },
  ],
});

console.log(`Created "${CHAT_TOPIC}" chat: ${newChat.id}`);
