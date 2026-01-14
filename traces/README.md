# Traces for hero-sim experiments

Este directorio contiene trazas sintéticas usadas por el CLI `hero-sim` y por los tests.
Están diseñadas para explorar patrones patológicos y de interés de la granja de render:

- `burst.json`: ráfagas de jobs simultáneos que ponen presión al scheduler.
- `starvation.json`: jobs grandes que pueden causar starving a jobs pequeños posteriores.
- `throttle.json`: job + subida rápida de temperatura (throttling) que exige replan.
- `clustered_deadlines.json`: varios deadlines cercanos que retan a EDF.
- `backfill.json`: muchos jobs pequeños que deben ser backfilled eficientemente.
- `ramp.json`: carga que aumenta en el tiempo (ramp-up) para evaluar adaptación.
- `mem_pressure.json`: presión de memoria simulada que provoca mem_warn/mem_crit.
- `offline.json`: dispositivo pasa a estado degradado/offline y vuelve a la normalidad.

Uso rápido:

```bash
# correr una simulación y exportar un reporte + gráfica
python -m 20_BLENDER_INTEGRATION.hero.cli --trace traces/burst.json --policy greedy --report out/report.json --plot out/timeline.png
```

Estas trazas son el punto de partida; podemos añadir más casos patológicos según vayamos encontrando fallos en políticas o como dataset para entrenamiento offline.
