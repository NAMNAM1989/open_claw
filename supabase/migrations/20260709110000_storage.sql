-- Storage buckets cho open_claw
-- Chạy sau migration initial

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values
  (
    'qr-images',
    'qr-images',
    false,
    5242880,
    array['image/png', 'image/jpeg', 'image/webp']
  ),
  (
    'documents',
    'documents',
    false,
    10485760,
    array['image/png', 'image/jpeg', 'image/webp', 'application/pdf']
  )
on conflict (id) do nothing;

-- Chỉ service role upload — không public read
