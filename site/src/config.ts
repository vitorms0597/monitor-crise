/** Caminho interno com o prefixo do site (ex.: /monitor-crise no GitHub Pages; vazio em domínio próprio). */
export const u = (path: string) => `${import.meta.env.BASE_URL.replace(/\/$/, '')}${path}`;

export const SITE_NAME = 'Monitor de Crises';
export const SITE_URL = new URL(import.meta.env.BASE_URL, import.meta.env.SITE).toString();
export const SITE_DESCRIPTION =
  'Ciberataques, guerras, apagões e desastres no mundo, atualizados a cada 30 minutos a partir de fontes primárias, com mapa de calor por país.';

// Anúncios: deixe vazio até a conta ser aprovada; os espaços continuam reservados no layout.
export const ADSENSE_CLIENT = import.meta.env.PUBLIC_ADSENSE_CLIENT ?? '';
export const AADS_UNIT = import.meta.env.PUBLIC_AADS_UNIT ?? '';
export const CONTACT_EMAIL: string = import.meta.env.PUBLIC_CONTACT_EMAIL ?? '';
// sem e-mail configurado, o contato é por issues do repositório público
export const CONTACT_URL = CONTACT_EMAIL ? `mailto:${CONTACT_EMAIL}` : 'https://github.com/vitorms0597/monitor-crise/issues';
export const CONTACT_LABEL = CONTACT_EMAIL || 'issues do projeto no GitHub';

export type TemaId = 'ciber' | 'conflito' | 'energia' | 'desastre';

export const TEMAS: {
  id: TemaId;
  slug: string;
  nome: string;
  curto: string;
  descricao: string;
}[] = [
  {
    id: 'conflito',
    slug: 'guerras-e-conflitos',
    nome: 'Guerras e conflitos',
    curto: 'Conflito',
    descricao: 'ataques armados, bombardeios, mísseis, drones e terrorismo',
  },
  {
    id: 'ciber',
    slug: 'ciberataques',
    nome: 'Ciberataques',
    curto: 'Ciber',
    descricao: 'ataques hacker, ransomware, vazamentos de dados e falhas exploradas',
  },
  {
    id: 'energia',
    slug: 'apagoes',
    nome: 'Apagões',
    curto: 'Energia',
    descricao: 'quedas de energia e falhas na rede elétrica',
  },
  {
    id: 'desastre',
    slug: 'desastres',
    nome: 'Desastres naturais',
    curto: 'Desastre',
    descricao: 'terremotos, enchentes, ciclones, incêndios florestais e vulcões',
  },
];

export const temaById = Object.fromEntries(TEMAS.map((t) => [t.id, t])) as Record<TemaId, (typeof TEMAS)[number]>;

export const SUBTEMAS: Record<string, string> = {
  guerra: 'guerra',
  terrorismo: 'terrorismo',
  ataque: 'ataque hacker',
  ransomware: 'ransomware',
  vazamento: 'vazamento de dados',
  vulnerabilidade: 'falha explorada',
  apagao: 'apagão',
  terremoto: 'terremoto',
  enchente: 'enchente',
  ciclone: 'ciclone',
  incendio: 'incêndio florestal',
  vulcao: 'vulcão',
  tsunami: 'tsunami',
  deslizamento: 'deslizamento',
  tempestade: 'tempestade',
  seca: 'seca',
};
