import { createClient } from '@supabase/supabase-js';

const DEFAULT_SUPABASE_URL = 'https://oogcmsouczrmbwughnfb.supabase.co';
const DEFAULT_SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9vZ2Ntc291Y3pybWJ3dWdobmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ3MjIwNzMsImV4cCI6MjEwMDI5ODA3M30.qvLLoL-yhrKluw8Yu0GwqUfRA4FQ4doFUb-opnv3sBc';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || DEFAULT_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || DEFAULT_SUPABASE_ANON_KEY;

export const isSupabaseConfigured = Boolean(
  supabaseUrl && 
  supabaseAnonKey && 
  supabaseAnonKey !== 'your-supabase-anon-key-here' &&
  !supabaseAnonKey.includes('placeholder')
);

// Production client configured with verified Supabase credentials
export const supabase = createClient(
  supabaseUrl,
  supabaseAnonKey,
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    }
  }
);

export async function getCurrentAccessToken(): Promise<string | null> {
  try {
    const { data: { session }, error } = await supabase.auth.getSession();
    if (error || !session) return null;
    return session.access_token;
  } catch {
    return null;
  }
}
