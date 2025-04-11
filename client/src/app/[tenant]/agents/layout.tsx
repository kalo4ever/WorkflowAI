import { TenantID } from '@/types/aliases';

export async function generateMetadata({ params }: { params: { tenant: TenantID } }) {
  return {
    title: `AI agents · ${decodeURIComponent(params.tenant)}`,
  };
}

export default function TaskLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <div className='h-full w-full'>{children}</div>;
}
