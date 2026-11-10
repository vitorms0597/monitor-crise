// Textos factuais gerados a partir dos dados (sem adjetivos, só números e fontes).
import { SUBTEMAS, TEMAS, type TemaId } from '../config';
import { countryName, events, heat, newsCount, type Item } from './data';
import { num } from './format';

const listJoin = (xs: string[]) => (xs.length <= 1 ? xs.join('') : `${xs.slice(0, -1).join(', ')} e ${xs.at(-1)}`);

export function countrySummary(iso: string) {
  const name = countryName(iso);
  const p = heat('24h').paises[iso];
  const n24 = TEMAS.map((t) => ({ t, n: newsCount(iso, t.id, 24) })).filter((x) => x.n > 0).sort((a, b) => b.n - a.n);
  const since = Date.now() - 7 * 24 * 3600_000;
  const official = events().filter((e) => e.pais_iso === iso && new Date(e.atualizado_em).getTime() >= since);
  const out: string[] = [];
  if (n24.length) {
    out.push(
      `Nas últimas 24 horas, o Monitor contabilizou ${listJoin(n24.map((x) => `${num(x.n)} registros de ${x.t.nome.toLowerCase()}`))} ligados a ${name}.`,
    );
  } else {
    out.push(`Nas últimas 24 horas não houve registros ligados a ${name} nos quatro temas monitorados.`);
  }
  if (p && p.anterior > 0 && p.variacao !== null) {
    out.push(
      `O volume total ${p.variacao >= 0 ? 'subiu' : 'caiu'} ${num(Math.abs(p.variacao))}% em relação às 24 horas anteriores (${num(p.anterior)} → ${num(p.total)}).`,
    );
  }
  if (official.length) {
    const kinds = countBy(official.map((e) => SUBTEMAS[e.subtema] ?? e.subtema));
    out.push(
      `Fontes oficiais registraram ${num(official.length)} ${official.length === 1 ? 'evento' : 'eventos'} nos últimos 7 dias: ${listJoin(
        kinds.map(([k, n]) => `${num(n)} de ${k}`),
      )}.`,
    );
    const worst = official.reduce((a, b) => (b.severidade > a.severidade ? b : a));
    if (worst.severidade >= 3) out.push(`O mais grave: ${worst.titulo} (nível ${worst.severidade} de 5, fonte ${worst.fonte}).`);
  }
  return out;
}

export function temaSummary(tema: TemaId) {
  const t = TEMAS.find((x) => x.id === tema)!;
  const h = heat('24h');
  const n24 = newsCount(null, tema, 24);
  const top = Object.entries(h.paises)
    .map(([iso, p]) => ({ iso, v: p.temas[tema] ?? 0 }))
    .filter((x) => x.v > 0)
    .sort((a, b) => b.v - a.v)
    .slice(0, 3);
  const out = [`Este painel reúne ${t.descricao}. Nas últimas 24 horas foram ${num(n24)} registros no mundo.`];
  if (top.length) out.push(`Os países com mais registros: ${listJoin(top.map((x) => `${countryName(x.iso)} (${num(x.v)})`))}.`);
  return out;
}

export function eventDescription(e: Item) {
  return `${e.titulo}. Registro da fonte oficial ${e.fonte}, nível ${e.severidade} de 5 na escala do Monitor de Crises.`;
}

function countBy(xs: string[]) {
  const m = new Map<string, number>();
  for (const x of xs) m.set(x, (m.get(x) ?? 0) + 1);
  return [...m.entries()].sort((a, b) => b[1] - a[1]);
}
