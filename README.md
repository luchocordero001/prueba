# Descarga automatizada de ENDES (INEI)

Este repositorio incluye un script en Python para descargar archivos de la encuesta ENDES desde URLs del INEI.

## Requisitos

- Python 3.10+

## Uso

Descargar uno o varios archivos con `--url`:

```bash
python scripts/download_endes.py \
  --url "https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1873/" \
  --output-dir data/raw
```

Si el servidor requiere cabeceras adicionales (por ejemplo, `Referer`), puedes usar:

```bash
python scripts/download_endes.py \
  --url "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/SPSS/968-Modulo1629.zip" \
  --referer "https://proyectos.inei.gob.pe/" \
  --output-dir data/raw
```

También puedes enviar cabeceras arbitrarias con `--header "Nombre: Valor"`.

Descargar múltiples archivos listados en un archivo de texto:

```bash
# urls.txt
# Una URL por línea
https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1873/

python scripts/download_endes.py --url-file urls.txt --output-dir data/raw
```

El script valida:
- Código HTTP 200.
- Tamaño distinto de cero.

Si algo falla, el script reporta el error y devuelve un código de salida distinto de cero.
