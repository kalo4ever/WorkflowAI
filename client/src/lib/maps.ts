export function getWithDefault<K, V>(
  map: Map<K, V>,
  key: K,
  defaultValue: () => V
): V {
  const current = map.get(key);
  if (current !== undefined) {
    return current;
  }

  const def = defaultValue();
  map.set(key, def);
  return def;
}
