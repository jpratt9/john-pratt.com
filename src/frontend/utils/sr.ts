// eslint-disable-next-line @typescript-eslint/no-explicit-any
let instance: any = null;

export async function getSr(): Promise<any> {
  if (typeof window === 'undefined') return null;
  if (instance) return instance;

  const { default: ScrollReveal } = await import('scrollreveal');
  instance = ScrollReveal();
  return instance;
}
