import fs from 'node:fs';
import path from 'node:path';
import { geoEqualEarth, geoGraticule10, geoPath } from 'd3-geo';

export const MAP_W = 1000;
export const MAP_H = 440;

type Feature = { type: 'Feature'; properties: { iso3: string; nome: string }; geometry: unknown };

let cache: { shapes: { iso3: string; nome: string; d: string }[]; graticule: string; project: (lon: number, lat: number) => [number, number] | null } | null = null;

export function worldMap() {
  if (cache) return cache;
  const file = path.resolve(process.cwd(), 'public', 'geo', 'countries-110m.geojson');
  const fc = JSON.parse(fs.readFileSync(file, 'utf8')) as { type: 'FeatureCollection'; features: Feature[] };
  fc.features = fc.features.filter((f) => f.properties.iso3 !== 'ATA');
  const projection = geoEqualEarth().fitExtent(
    [
      [4, 4],
      [MAP_W - 4, MAP_H - 4],
    ],
    fc as never,
  );
  const p = geoPath(projection).digits(1);
  cache = {
    shapes: fc.features.map((f) => ({ iso3: f.properties.iso3, nome: f.properties.nome, d: p(f as never) ?? '' })),
    graticule: p(geoGraticule10() as never) ?? '',
    project: (lon, lat) => projection([lon, lat]) as [number, number] | null,
  };
  return cache;
}
