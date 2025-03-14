export function formatJoinedEnvironments(envs?: string[]) {
  if (!envs?.length) return '';
  const capitalize = (str: string) =>
    str.charAt(0).toUpperCase() + str.slice(1);
  const capitalizedEnvs = envs.map(capitalize);
  if (capitalizedEnvs.length === 1) return capitalizedEnvs[0];
  return `${capitalizedEnvs.slice(0, -1).join(', ')} and ${capitalizedEnvs[capitalizedEnvs.length - 1]}`;
}
