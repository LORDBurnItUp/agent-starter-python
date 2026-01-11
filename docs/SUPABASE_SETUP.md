# Supabase Setup Guide

This guide will help you set up Supabase for data persistence in your LiveKit Agent project. **Supabase is completely optional** - your agent will work fine without it.

## Why Use Supabase?

Supabase provides a free PostgreSQL database perfect for:
- Storing conversation history
- Saving user preferences
- Tracking agent metrics
- Persisting any custom data your agent needs

## Free Tier

Supabase offers a generous free tier that includes:
- 500 MB database space
- 1 GB file storage
- 2 GB bandwidth
- 50,000 monthly active users
- Unlimited API requests

Perfect for development and small-scale production!

## Setup Steps

### 1. Create a Supabase Account

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub (recommended) or email

### 2. Create a New Project

1. Click "New Project"
2. Choose your organization (or create one)
3. Enter project details:
   - **Name**: `livekit-agent` (or whatever you prefer)
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Free tier is perfect to start

### 3. Get Your API Keys

Once your project is ready (takes ~2 minutes):

1. Go to Project Settings (gear icon) → API
2. Copy these values:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY`
   - **service_role** key → `SUPABASE_SERVICE_KEY` (keep this secret!)

### 4. Set Up Database Schema

1. In Supabase Dashboard, go to SQL Editor
2. Open the `src/supabase/schema.sql` file from this project
3. Copy the entire contents
4. Paste into Supabase SQL Editor
5. Click "Run"

This creates tables for:
- Conversations
- Messages
- User preferences
- Agent metrics

### 5. Configure Environment Variables

Add to your `.env.local` file:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

### 6. Install Supabase Client

```bash
uv add supabase
```

## Using Supabase in Your Agent

```python
from src.supabase import get_supabase_client

# Get client (returns None if not configured)
supabase = get_supabase_client()

if supabase:
    # Store a conversation
    conversation = supabase.table('conversations').insert({
        'session_id': 'abc123',
        'room_name': 'my-room',
        'participant_identity': 'user@example.com'
    }).execute()

    # Store messages
    message = supabase.table('messages').insert({
        'conversation_id': conversation.data[0]['id'],
        'role': 'user',
        'content': 'Hello, agent!'
    }).execute()

    # Query conversations
    recent = supabase.table('conversations') \
        .select('*') \
        .order('started_at', desc=True) \
        .limit(10) \
        .execute()
```

## Optional: Enable Realtime

For real-time updates (like live dashboards):

1. Go to Database → Replication
2. Enable replication for your tables
3. Use Supabase realtime subscriptions in your code

## Security Best Practices

1. **Never commit** `.env.local` to git
2. Use **service_role** key only in server-side code
3. Set up proper **Row Level Security (RLS)** policies for production
4. Rotate keys if they're ever exposed

## Troubleshooting

### "supabase module not found"
```bash
uv add supabase
```

### "Invalid API key"
- Double-check your `.env.local` file
- Make sure you copied the full key
- Verify project URL is correct

### "Permission denied"
- Check Row Level Security policies in Supabase Dashboard
- Ensure you're using service_role key for server operations

## Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

## Going to Production

When deploying to production:

1. Upgrade to a paid plan if needed (starts at $25/month)
2. Set up proper authentication
3. Configure RLS policies based on your auth
4. Enable Point-in-Time Recovery (PITR) for backups
5. Monitor usage in Supabase Dashboard
