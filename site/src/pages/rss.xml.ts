import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { SITE_DESCRIPTION, SITE_NAME, SUBTEMAS, u } from '../config';
import { countryName, eventSlug, featuredEvents } from '../lib/data';
import { eventDescription } from '../lib/texts';

export function GET(context: APIContext) {
  const items = [...featuredEvents()].sort((a, b) => b.atualizado_em.localeCompare(a.atualizado_em)).slice(0, 50);
  return rss({
    title: SITE_NAME,
    description: SITE_DESCRIPTION,
    site: new URL(import.meta.env.BASE_URL, context.site!).toString(),
    items: items.map((e) => ({
      title: e.titulo,
      link: u(`/evento/${eventSlug(e.id)}/`),
      pubDate: new Date(e.publicado_em),
      description: eventDescription(e),
      categories: [SUBTEMAS[e.subtema] ?? e.subtema, countryName(e.pais_iso)],
    })),
    customData: '<language>pt-br</language>',
  });
}
