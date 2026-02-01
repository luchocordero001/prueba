# Troubleshooting

## 403 CONNECT tunnel errors

In this environment, a HEAD request to the INEI download URL returned a CONNECT tunnel 403.

```bash
curl -I "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/SPSS/968-Modulo1629.zip"
```

Result:

```
curl: (56) CONNECT tunnel failed, response 403
HTTP/1.1 403 Forbidden
```

This indicates a network/proxy restriction in the execution environment rather than an application bug.
