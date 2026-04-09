import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY;

export const supabase = createClient(supabaseUrl, supabaseKey);

/**
 * Fetch orders directly from Supabase
 */
export const getOrdersDirectly = async () => {
  try {
    const { data, error } = await supabase
      .from('orders')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) throw error;

    return {
      success: true,
      orders: data || [],
      count: data?.length || 0
    };
  } catch (error) {
    console.error('Supabase error:', error);
    throw error;
  }
};

/**
 * Get orders count from Supabase
 */
export const getOrdersCount = async () => {
  try {
    const { count, error } = await supabase
      .from('orders')
      .select('*', { count: 'exact', head: true });

    if (error) throw error;
    return count || 0;
  } catch (error) {
    console.error('Supabase error:', error);
    return 0;
  }
};
