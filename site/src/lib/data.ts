// Lê os arquivos gerados pelo coletor (../data por padrão). Tudo roda no build.
import fs from 'node:fs';
import path from 'node:path';
import { TEMAS, type TemaId } from '../config';

const ROOT = path.resolve(process.cwd(), '..');
const DATA = path.resolve(process.env.DATA_DIR ?? path.join(ROOT, 'data'));
const GEO = path.join(ROOT, 'collector', 'geo', 'countries.json');

export const EVENT_POINTS: Record<number, number> = { 1: 1, 2: 3, 3: 6, 4: 10, 5: 15 };
export const HOURS = 72;

export type Item = {
  id: string;
  tipo: 'evento' | 'noticia';
  tema: TemaId;
  subtema: string;
  titulo: string;
  fonte: string;
  fonte_url: string;
  publicado_em: string;
  atualizado_em: string;
  severidade: number;
  pais_iso: string | null;
  lat: number | null;
  lon: number | null;
  idioma: string;
};

export type Country = {
  iso3: string;
  iso2: string | null;
  nome: string;
  nome_en: string;
  slug: string;
  continente: string;
  centro: [number, number];
};

type Scores = { total: number; temas: Record<TemaId, number>; noticias: number; eventos: number; anterior: number; variacao: number | null };
export type Heat = { gerado_em: string; janela: string; temas: Record<TemaId, number>; paises: Record<string, Scores>; ranking: string[]; subindo: string[] };

function read<T>(file: string, fallback: T): T {
  try {
    return JSON.parse(fs.readFileSync(path.join(DATA, file), 'utf8')) as T;
  } catch {
    return fallback;
  }
}

const memo = new Map<string, unknown>();
function cached<T>(key: string, fn: () => T): T {
  if (!memo.has(key)) memo.set(key, fn());
  return memo.get(key) as T;
}

export const countries = () =>
  cached('countries', () => {
    const list = JSON.parse(fs.readFileSync(GEO, 'utf8')) as Country[];
    return Object.fromEntries(list.map((c) => [c.iso3, c])) as Record<string, Country>;
  });

export const countryName = (iso: string | null) => (iso && countries()[iso]?.nome) || 'Mundo';

const emptyHeat = (janela: string): Heat => ({
  gerado_em: new Date().toISOString(),
  janela,
  temas: { ciber: 0, conflito: 0, energia: 0, desastre: 0 },
  paises: {},
  ranking: [],
  subindo: [],
});
export const heat = (janela: '24h' | '7d') => cached(`heat${janela}`, () => read<Heat>(`agg/heat_${janela}.json`, emptyHeat(janela)));
export const events = () => cached('events', () => read<Item[]>('events.json', []));
export const news = () => cached('news', () => read<Item[]>('news.json', []));
export const state = () => cached('state', () => read<{ ultima_coleta?: string; falhas?: string[] }>('state.json', {}));

export const updatedAt = () => new Date(state().ultima_coleta ?? heat('24h').gerado_em);

/** Horas cheias (UTC) das últimas `HOURS` horas, terminando na hora da última coleta. */
export const hourAxis = () =>
  cached('axis', () => {
    const end = new Date(updatedAt());
    end.setUTCMinutes(0, 0, 0);
    return Array.from({ length: HOURS }, (_, i) => new Date(end.getTime() - (HOURS - 1 - i) * 3600_000));
  });

type HourBuckets = Record<string, Record<TemaId, number[]>>; // iso -> tema -> valores por hora

/** Série horária (notícias + pontos de eventos) por país e tema, a partir de data/counts. */
export const hourly = () =>
  cached('hourly', () => {
    const axis = hourAxis();
    const index = new Map(axis.map((d, i) => [d.toISOString().slice(0, 13), i]));
    const out: HourBuckets = {};
    const bucket = (iso: string) =>
      (out[iso] ??= Object.fromEntries(TEMAS.map((t) => [t.id, new Array(axis.length).fill(0)])) as Record<TemaId, number[]>);
    const days = [...new Set(axis.map((d) => d.toISOString().slice(0, 10)))];
    for (const day of days) {
      const data = read<Record<string, Record<string, Record<string, number>>>>(`counts/${day}.json`, {});
      for (const [hh, byCountry] of Object.entries(data)) {
        const i = index.get(`${day}T${hh}`);
        if (i === undefined) continue;
        for (const [iso, temas] of Object.entries(byCountry))
          for (const [tema, n] of Object.entries(temas)) bucket(iso)[tema as TemaId][i] += n;
      }
    }
    for (const e of events()) {
      const i = index.get(e.atualizado_em.slice(0, 13));
      if (i === undefined || !e.pais_iso) continue;
      bucket(e.pais_iso)[e.tema][i] += EVENT_POINTS[e.severidade] ?? 1;
    }
    return out;
  });

/** Soma das séries de todos os países, por tema. */
export const hourlyWorld = () =>
  cached('hourlyWorld', () => {
    const axis = hourAxis();
    const out = Object.fromEntries(TEMAS.map((t) => [t.id, new Array(axis.length).fill(0)])) as Record<TemaId, number[]>;
    for (const byTema of Object.values(hourly()))
      for (const t of TEMAS) byTema[t.id].forEach((v, i) => (out[t.id][i] += v));
    return out;
  });

/** Primeira hora com notícias contadas (antes disso o traço não existe, não é "calma"). */
export const collectingSince = () =>
  cached('since', () => {
    let first: string | null = null;
    let files: string[] = [];
    try {
      files = fs.readdirSync(path.join(DATA, 'counts')).filter((f) => f.endsWith('.json')).sort();
    } catch {}
    for (const f of files) {
      const hours = Object.keys(read<Record<string, unknown>>(`counts/${f}`, {})).sort();
      if (hours.length) {
        first = `${f.slice(0, 10)}T${hours[0]}:00:00Z`;
        break;
      }
    }
    return first ? new Date(first) : null;
  });

/** Índice no eixo de 72h a partir do qual há coleta. */
export const axisStart = () => {
  const since = collectingSince();
  if (!since) return hourAxis().length;
  const i = hourAxis().findIndex((d) => d.getTime() >= since.getTime());
  return i < 0 ? hourAxis().length : i;
};

/** "7 dias" só quando há 7 dias de coleta; antes disso, "desde 08/11". */
export const longWindowLabel = () => {
  const since = collectingSince();
  if (!since || updatedAt().getTime() - since.getTime() >= 7 * 24 * 3600_000 - 3600_000) return '7 dias';
  return `desde ${since.toLocaleDateString('pt-BR', { timeZone: 'America/Sao_Paulo', day: '2-digit', month: '2-digit' })}`;
};

export const eventSlug = (id: string) => id.replace(/[^a-zA-Z0-9]+/g, '-').toLowerCase();

/** Eventos oficiais que ganham página própria. */
export const featuredEvents = () => cached('featured', () => events().filter((e) => e.severidade >= 2 && e.tipo === 'evento'));

/** Países com volume suficiente para merecer página (evita página vazia). */
export const countryPages = () =>
  cached('countryPages', () => {
    const h7 = heat('7d');
    return Object.entries(h7.paises)
      .filter(([iso, p]) => p.total >= 5 && countries()[iso])
      .sort((a, b) => b[1].total - a[1].total)
      .map(([iso]) => countries()[iso]);
  });

export const hasCountryPage = (iso: string | null) => !!iso && countryPages().some((c) => c.iso3 === iso);

/** Lista mista (eventos oficiais + manchetes) do mais recente para o mais antigo, sem manchetes repetidas. */
export function feed(opts: { tema?: TemaId; iso?: string; limit?: number; since?: Date } = {}) {
  const { tema, iso, limit = 40, since } = opts;
  const all = [...events(), ...news()].filter(
    (e) => (!tema || e.tema === tema) && (!iso || e.pais_iso === iso) && (!since || new Date(e.atualizado_em) >= since),
  );
  all.sort((a, b) => b.atualizado_em.localeCompare(a.atualizado_em));
  return all.slice(0, limit);
}

export function newsCount(iso: string | null, tema: TemaId | null, hours: number) {
  const axis = hourAxis();
  const from = axis.length - hours;
  const sum = (arr: number[]) => arr.slice(Math.max(0, from)).reduce((a, b) => a + b, 0);
  if (iso) {
    const b = hourly()[iso];
    if (!b) return 0;
    return tema ? sum(b[tema]) : TEMAS.reduce((acc, t) => acc + sum(b[t.id]), 0);
  }
  const w = hourlyWorld();
  return tema ? sum(w[tema]) : TEMAS.reduce((acc, t) => acc + sum(w[t.id]), 0);
}
