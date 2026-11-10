const TZ = 'America/Sao_Paulo';

export const num = (n: number) => n.toLocaleString('pt-BR');

/** Variação: até +99% em porcentagem; acima disso como multiplicador ("×13,8"), que se lê de relance. */
export const pct = (v: number | null) => {
  if (v === null) return 'novo';
  if (v >= 100) return `×${(1 + v / 100).toLocaleString('pt-BR', { maximumFractionDigits: 1 })}`;
  return `${v > 0 ? '+' : ''}${num(v)}%`;
};

export const coords = (lat: number, lon: number) => {
  const f = (n: number) => Math.abs(n).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  return `${f(lat)}° ${lat >= 0 ? 'N' : 'S'}, ${f(lon)}° ${lon >= 0 ? 'L' : 'O'}`;
};

export const hora = (d: Date | string) =>
  new Date(d).toLocaleTimeString('pt-BR', { timeZone: TZ, hour: '2-digit', minute: '2-digit' });

export const dataHora = (d: Date | string) =>
  new Date(d).toLocaleString('pt-BR', { timeZone: TZ, day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }).replace(',', ' ·');

export const dataLonga = (d: Date | string) =>
  new Date(d).toLocaleDateString('pt-BR', { timeZone: TZ, day: 'numeric', month: 'long', year: 'numeric' });

export function relativo(d: Date | string, now: Date) {
  const min = Math.round((now.getTime() - new Date(d).getTime()) / 60000);
  if (min < 60) return `há ${Math.max(1, min)} min`;
  const h = Math.round(min / 60);
  if (h < 48) return `há ${h} h`;
  return `há ${Math.round(h / 24)} dias`;
}

export const IDIOMAS: Record<string, string> = { en: 'EN', es: 'ES', pt: 'PT', fr: 'FR', de: 'DE', it: 'IT' };
