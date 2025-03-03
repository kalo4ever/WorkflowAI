export function detectDevice(): 'Android' | 'iOS' | 'Desktop' {
  const userAgent = navigator.userAgent;
  if (/android/i.test(userAgent)) {
    return 'Android';
  }
  if (/iPad|iPhone|iPod/.test(userAgent)) {
    return 'iOS';
  }
  return 'Desktop';
}
