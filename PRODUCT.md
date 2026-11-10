# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Brasileiros que desconfiam da mídia tradicional e querem ver por conta própria o que está acontecendo no mundo: ciberataques, guerras/conflitos, apagões e desastres. Chegam pelo celular, via redes sociais e busca ("terremoto hoje", "apagão", "ataque hacker"), checam rápido onde está "esquentando" e voltam várias vezes ao dia.

## Product Purpose
Agregar em PT-BR, de vários países, eventos e cobertura de imprensa sobre crises e mostrar num mapa de calor quais temas estão sendo mais falados e onde. Sucesso = audiência recorrente e orgânica, monetizada por anúncios no próprio site.

## Positioning
Monitor independente: sem editorial nem opinião, só dados de fontes primárias (USGS, GDACS, NASA EONET, CISA, GDELT) com link para a origem, atualizados a cada 30 minutos. O visitante vê os números e tira as próprias conclusões.

## Operating Context
Visitas curtas e frequentes, majoritariamente mobile. Páginas por país e por tema são a porta de entrada via busca. Conteúdo gerado automaticamente; não há redação humana.

## Capabilities and Constraints
- Site 100% estático (Astro), reconstruído a cada coleta; dados em `data/*.json` gerados por `collector/`.
- 4 temas: ciber, conflito, energia, desastre. Janelas 24h e 7d.
- Infra a custo zero (GitHub Pages + GitHub Actions). Sem IA/resumos pagos por enquanto.
- Manchetes da imprensa vêm no idioma original (maioria inglês); textos do site em PT-BR.
- Espaços de anúncio previstos no layout (AdSense depois de aprovação; A-Ads antes).
- Blockchain (espelho IPFS, prova on-chain) é fase futura — não prometer no site ainda.

## Brand Commitments
- Nome: **Monitor de Crises**.
- Tom: frio e factual. Números e fatos, sem adjetivos alarmistas, sem "o que a mídia esconde".

## Evidence on Hand
Dados reais coletados em `data/` (eventos oficiais, notícias GDELT, agregados de calor). Não há depoimentos, imprensa, parceiros ou números de audiência — não inventar.

## Product Principles
1. Fato com fonte, sempre: todo item leva link para a origem.
2. Nada inventado ou inflado: o conteúdo precisa ser defensável para anunciantes e leitores.
3. Rápido no celular: o mapa e o "onde está esquentando" aparecem em segundos.
4. Cada país e tema tem uma página própria indexável.

## Accessibility & Inclusion
Cor nunca é o único canal de informação no mapa (ranking em texto ao lado); contraste AA no tema escuro.
