SELECT
  current_database() AS database_name,
  current_user AS connected_user,
  now() AS connected_at;
