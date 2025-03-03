import { MajorVersion, VersionV1 } from '@/types/workflowAI';

export type VersionEntry = {
  majorVersion: MajorVersion;
  versions: VersionV1[];
};

type FilterVersionsProps = {
  versions: VersionV1[];
  filterOption: 'deployed' | 'favorite' | undefined;
};

export function versionDictionary(props: FilterVersionsProps) {
  const { versions, filterOption } = props;

  const result: Record<string, VersionV1> = {};

  versions.forEach((version) => {
    switch (filterOption) {
      case 'deployed':
        if (!!version.deployments && version.deployments.length > 0) {
          result[version.id] = version;
        }
        break;
      case 'favorite':
        if (version.is_favorite) {
          result[version.id] = version;
        }
        break;
      default:
        result[version.id] = version;
        break;
    }
  });

  return result;
}

type FilterMajorVersionsProps = {
  majorVersions: MajorVersion[];
  versions: VersionV1[];
  filterOption: 'deployed' | 'favorite' | undefined;
};

export function filterVersions(props: FilterMajorVersionsProps) {
  const { majorVersions, versions, filterOption } = props;
  const result: VersionEntry[] = [];

  const filteredVersionsDictionary = versionDictionary({
    versions,
    filterOption,
  });

  majorVersions.forEach((majorVersion) => {
    const filteredVersions: VersionV1[] = [];

    majorVersion.minors.forEach((minor) => {
      const version = filteredVersionsDictionary[minor.id];
      if (version) {
        filteredVersions.push(version);
      }
    });

    if (filteredVersions.length === 0) {
      return;
    }

    result.push({
      majorVersion,
      versions: filteredVersions,
    });
  });

  result.sort((a, b) => b.majorVersion.major - a.majorVersion.major);
  return result;
}

export function numberOfVersions(entry: VersionEntry[]): number {
  return entry.reduce((acc, curr) => acc + curr.versions.length, 0);
}
