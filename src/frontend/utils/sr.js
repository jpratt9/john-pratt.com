let instance;
export async function getSr() {
  if (typeof window === 'undefined') return null;
  if (instance) return instance;
  const { default: ScrollReveal } = await import('scrollreveal');
  instance = ScrollReveal();
  return instance;
}
