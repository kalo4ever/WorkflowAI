import { usePathname } from 'next/navigation';
import { signInRoute, signUpRoute } from '@/lib/routeFormatter';
import { cn } from '@/lib/utils';
import { useAuth } from '../../lib/AuthContext';
import { Button } from './Button';

type LoginSignUpPlaceholderProps = {
  className?: string;
};

export function LoginSignUpPlaceholder(props: LoginSignUpPlaceholderProps) {
  const { className } = props;
  const pathname = usePathname();

  const routeForSignUp = signUpRoute({ forceRedirectUrl: pathname });
  const routeForSignIn = signInRoute({ forceRedirectUrl: pathname });

  const { isSignedIn } = useAuth();

  if (isSignedIn) {
    return null;
  }

  return (
    <div
      className={cn(
        'flex w-full h-full items-center justify-center',
        className
      )}
    >
      <div className='flex flex-wrap gap-2'>
        <Button variant='newDesign' toRoute={routeForSignIn}>
          Login
        </Button>
        <Button variant='newDesignIndigo' toRoute={routeForSignUp}>
          Sign up
        </Button>
      </div>
    </div>
  );
}
