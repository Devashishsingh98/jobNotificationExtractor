-- Migration: Add role field to users table
-- Run this if you already have the database set up

-- Add role column
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS role TEXT CHECK (role IN ('user', 'admin')) DEFAULT 'user';

-- Update existing users to have 'user' role if NULL
UPDATE public.users SET role = 'user' WHERE role IS NULL;
