import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = "https://pccdjaplsjxrifypznlb.supabase.co"
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBjY2RqYXBsc2p4cmlmeXB6bmxiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNzA1MDksImV4cCI6MjA3MDg0NjUwOX0.rZqjbob_cnCkrZ9HmZ7c4Sj9X4-863eNQqc0Q-fcKLI"

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
