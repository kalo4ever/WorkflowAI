export function isCompanyURL(str: string) {
  const domainPattern = /^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9](\.[a-zA-Z]{2,})+$/;

  let urlToTest = str.trim().toLowerCase();

  urlToTest = urlToTest.replace(/^(https?:\/\/)?(www\.)?/, '');

  if (!domainPattern.test(urlToTest)) {
    return false;
  }
  try {
    new URL(`https://${urlToTest}`);
    return true;
  } catch {
    return false;
  }
}

export function capitalizeCompanyURL(text: string) {
  return text
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}
