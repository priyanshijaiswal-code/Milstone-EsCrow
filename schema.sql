create table contracts (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  brief text not null,
  freelancer_email text,
  client_email text,
  created_at timestamptz default now()
);

create table milestones (
  id uuid primary key default gen_random_uuid(),
  contract_id uuid references contracts(id) on delete cascade,
  position int not null,
  title text not null,
  amount numeric(10,2) not null,
  checklist jsonb not null default '[]',   -- [{id, text}]
  status text not null default 'created',  -- created|awaiting_approval|funded|submitted|verified|released|voided|disputed
  paypal_order_id text,
  paypal_authorization_id text,
  authorized_at timestamptz
);

create table deliverables (
  id uuid primary key default gen_random_uuid(),
  milestone_id uuid references milestones(id) on delete cascade,
  live_url text,
  repo_url text,
  notes text,
  submitted_at timestamptz default now()
);

create table verifications (
  id uuid primary key default gen_random_uuid(),
  deliverable_id uuid references deliverables(id) on delete cascade,
  results jsonb not null,        -- [{item_id, pass, evidence}]
  recommendation text not null,  -- release|hold
  summary text,
  created_at timestamptz default now()
);

create table paypal_events (
  id uuid primary key default gen_random_uuid(),
  milestone_id uuid references milestones(id),
  event_type text,
  payload jsonb,
  created_at timestamptz default now()
);
