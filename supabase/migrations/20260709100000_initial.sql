-- open_claw — schema khởi tạo (Supabase project: open_claw)
-- Chạy: supabase db push  hoặc SQL Editor trên dashboard

-- Extensions
create extension if not exists "pgcrypto";

-- ─── Bookings & jobs ───────────────────────────────────────────────

create table if not exists public.bookings (
  id uuid primary key default gen_random_uuid(),
  chat_id bigint not null,
  raw_text text not null,
  vehicle_no text default '',
  flight text default '',
  flight_date text default '',
  destination text default '',
  mawb text default '',
  pcs int default 0,
  gross_weight numeric(12, 3) default 0,
  status text not null default 'pending'
    check (status in ('pending', 'running', 'done', 'error', 'cancelled')),
  error_message text default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists bookings_chat_id_idx on public.bookings (chat_id);
create index if not exists bookings_mawb_idx on public.bookings (mawb);
create index if not exists bookings_status_idx on public.bookings (status);

create table if not exists public.job_runs (
  id uuid primary key default gen_random_uuid(),
  booking_id uuid references public.bookings (id) on delete set null,
  chat_id bigint not null,
  registration_no text default '',
  vct_number text default '',
  verify_code text default '',
  status_text text default '',
  error_raw text default '',
  started_at timestamptz not null default now(),
  finished_at timestamptz
);

create index if not exists job_runs_chat_id_idx on public.job_runs (chat_id);
create index if not exists job_runs_reg_idx on public.job_runs (registration_no);

-- ─── Scale tickets & documents ───────────────────────────────────────

create table if not exists public.scale_tickets (
  id uuid primary key default gen_random_uuid(),
  chat_id bigint not null,
  awb text default '',
  flight text default '',
  flight_date text default '',
  pieces int default 0,
  gross_kg numeric(12, 3) default 0,
  chargeable_kg numeric(12, 3) default 0,
  form_type text default '',
  source text default '',
  raw_json jsonb default '{}',
  created_at timestamptz not null default now()
);

create index if not exists scale_tickets_chat_id_idx on public.scale_tickets (chat_id);
create index if not exists scale_tickets_awb_idx on public.scale_tickets (awb);

-- ─── Tariffs & quotes (gói B — chứng từ & báo giá) ─────────────────

create table if not exists public.tariffs (
  id uuid primary key default gen_random_uuid(),
  chat_id bigint not null,
  doc_type text default 'price_table',
  source text default '',
  rows_json jsonb not null default '[]',
  notes text default '',
  created_at timestamptz not null default now()
);

create index if not exists tariffs_chat_id_idx on public.tariffs (chat_id);

create table if not exists public.quotes (
  id uuid primary key default gen_random_uuid(),
  quote_code text not null unique,
  chat_id bigint not null,
  tariff_id uuid references public.tariffs (id) on delete set null,
  route text not null,
  cargo_type text default 'general',
  actual_kg numeric(12, 3) not null,
  volumetric_kg numeric(12, 3),
  chargeable_kg numeric(12, 3) not null,
  currency text not null default 'VND',
  total_amount numeric(14, 2) not null,
  breakdown_json jsonb not null default '{}',
  created_at timestamptz not null default now()
);

create index if not exists quotes_chat_id_idx on public.quotes (chat_id);
create index if not exists quotes_code_idx on public.quotes (quote_code);

-- ─── Customers & ops ─────────────────────────────────────────────────

create table if not exists public.customers (
  registration_no text primary key,
  customer_name text not null default '',
  updated_at timestamptz not null default now()
);

create table if not exists public.chat_sessions (
  chat_id bigint primary key,
  openclaw_user_key text not null default '',
  last_message_at timestamptz not null default now()
);

create table if not exists public.ops_log (
  id uuid primary key default gen_random_uuid(),
  level text not null default 'info'
    check (level in ('debug', 'info', 'warn', 'error')),
  source text not null default 'bot',
  message text not null,
  meta_json jsonb default '{}',
  created_at timestamptz not null default now()
);

create index if not exists ops_log_created_idx on public.ops_log (created_at desc);
create index if not exists ops_log_level_idx on public.ops_log (level);

-- ─── updated_at trigger ──────────────────────────────────────────────

create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists bookings_updated_at on public.bookings;
create trigger bookings_updated_at
  before update on public.bookings
  for each row execute function public.set_updated_at();

-- ─── RLS: chỉ service role (bot) — không anon client ─────────────────

alter table public.bookings enable row level security;
alter table public.job_runs enable row level security;
alter table public.scale_tickets enable row level security;
alter table public.tariffs enable row level security;
alter table public.quotes enable row level security;
alter table public.customers enable row level security;
alter table public.chat_sessions enable row level security;
alter table public.ops_log enable row level security;

-- Không tạo policy cho anon/authenticated → chỉ service_role truy cập được.
