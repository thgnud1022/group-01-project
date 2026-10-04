import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const isSupabaseConfigured = Boolean(
  supabaseUrl && 
  supabaseAnonKey && 
  supabaseAnonKey !== 'your-supabase-anon-key-here' &&
  !supabaseAnonKey.includes('placeholder')
);

// Fallback to placeholder if env variables are not yet provided by human setup
export const supabase = createClient(
  supabaseUrl || 'https://sthjkfssmvoswocnttrw.supabase.co',
  supabaseAnonKey || 'placeholder-anon-key-pending-human-setup',
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
