# Laboratorio 7 — BYB vs Placa, comparación por variable aislada

Comparaciones de señales EMG (BYB vs placa de 3 canales, cuarto aves vs cuarto ñandú) armadas para aislar, una por una, 
las variables que podían explicar diferencias entre mediciones: cuarto, computadora y dispositivo.

## Comparaciones

**1. BYB — cuarto aves (Clase 5) vs cuarto ñandú (Clase 7)**
Misma compu (trasladada de aves a ñandú para Clase 7), mismo dispositivo. Aísla el efecto del cuarto.
- [Belly](https://petrapastorino.github.io/Laboratorio-7-Byb-vs-placa-resumen/belly_cuarto_aves_vs_nandu.html)
- [Oris](https://petrapastorino.github.io/Laboratorio-7-Byb-vs-placa-resumen/oris_cuarto_aves_vs_nandu.html)
- [Plat](https://petrapastorino.github.io/Laboratorio-7-Byb-vs-placa-resumen/plat_cuarto_aves_vs_nandu.html)
- [Zygo](https://petrapastorino.github.io/Laboratorio-7-Byb-vs-placa-resumen/zygo_cuarto_aves_vs_nandu.html)

Generado por: `comparar_byb_aves_vs_nandu.py`

**2. Placa — Clase 5 (cuarto ñandú) vs Clase 6 (cuarto aves)**
Cuarto y compu cambian juntos (cada cuarto tenía su propia compu). No aísla una sola variable — se deja como referencia, no como comparación limpia.
- [Plat](https://petrapastorino.github.io/Laboratorio-7-Byb-vs-placa-resumen/plat_placa_clase5_vs_clase6.html)
- [Oris](https://petrapastorino.github.io/Laboratorio-7-Byb-vs-placa-resumen/oris_placa_clase5_vs_clase6.html)
- [Zygo](https://petrapastorino.github.io/Laboratorio-7-Byb-vs-placa-resumen/zygo_placa_clase5_vs_clase6.html)

Generado por: `comparar_placa_clase5_vs_clase6.py`

**3. Placa (Clase 6) vs BYB (Clase 5) — mismo cuarto (aves), misma compu**
Aísla el efecto del dispositivo. Las señales están normalizadas a su propio pico (placa y BYB no son comparables en amplitud absoluta, solo en forma).
- [Oris](https://petrapastorino.github.io/Laboratorio-7-Byb-vs-placa-resumen/oris_placa_clase6_vs_byb_clase5.html)
- [Plat](https://petrapastorino.github.io/Laboratorio-7-Byb-vs-placa-resumen/plat_placa_clase6_vs_byb_clase5.html)
- [Zygo](https://petrapastorino.github.io/Laboratorio-7-Byb-vs-placa-resumen/zygo_placa_clase6_vs_byb_clase5.html)

Generado por: `comparar_placa_clase6_vs_byb_clase5.py`

## Cómo usar los gráficos
- Botón arriba para alternar entre señal cruda y envolvente de Hilbert (40ms).
- Leyenda interactiva: click prende/apaga cada serie; la última que clickeás pasa a dibujarse arriba de la otra.
- Verde/naranja = cuarto (comparaciones 1 y 2). Otros colores = dispositivo (comparación 3).

## Otros scripts
`cociente_amplitud_bateria.py` — calcula el cociente de amplitud (RMS y pico de envolvente) entre Clase 7 y Clase 5 del BYB, músculo por vocal, para chequear si la diferencia de amplitud entre esas dos clases es consistente con un cambio de batería (escalado uniforme) o si hay algo específico de algún músculo/canal.
