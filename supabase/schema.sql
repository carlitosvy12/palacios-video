-- Palacios Video - esquema MVP para suscripciones y uso.
-- Ejecutar en Supabase SQL Editor.

create extension if not exists pgcrypto;

create table if not exists public.suscripciones (
  user_id uuid primary key references auth.users(id) on delete cascade,
  plan text not null check (plan in ('creator', 'pro', 'agencia')),
  stripe_customer_id text,
  stripe_subscription_id text,
  estado text not null default 'inactive',
  horas_limite numeric(8, 2) not null default 0,
  renovacion timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.uso_mensual (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  mes date not null,
  minutos_procesados numeric(10, 2) not null default 0,
  video_nombre text,
  created_at timestamptz not null default now()
);

create index if not exists uso_mensual_user_mes_idx
  on public.uso_mensual (user_id, mes);

alter table public.suscripciones enable row level security;
alter table public.uso_mensual enable row level security;

drop policy if exists "Usuarios ven su suscripcion" on public.suscripciones;
create policy "Usuarios ven su suscripcion"
  on public.suscripciones for select
  using (auth.uid() = user_id);

drop policy if exists "Usuarios ven su uso" on public.uso_mensual;
create policy "Usuarios ven su uso"
  on public.uso_mensual for select
  using (auth.uid() = user_id);

create or replace function public.minutos_usados_mes(p_user_id uuid, p_mes date)
returns numeric
language sql
stable
as $$
  select coalesce(sum(minutos_procesados), 0)
  from public.uso_mensual
  where user_id = p_user_id
    and mes = date_trunc('month', p_mes)::date;
$$;
