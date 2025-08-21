# Changelog

Todas las modificaciones notables a este proyecto se documentarán en este archivo.
El formato sigue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-08-21
### Added
- Soporte de **paginación** en ISPCube con `limit` y `offset`.
- Variable de entorno `ISPCUBE_LIMIT` para configurar tamaño de página por defecto (fallback a `100`).
- Logs de depuración adicionales: URL final de la request, headers de respuesta y claves del JSON.

### Changed
- `obtener_clientes_ispcube()` ahora **acumula todas las páginas** y devuelve una **lista completa** de clientes.
- Normalización de respuesta para aceptar lista directa o estructuras con `{"data": ...}`.

### Fixed
- Manejo robusto de **JSON nulo/ inválido** (evita `NoneType is not iterable`).
- Corrección de errores de control de flujo: `break` y `except` ahora dentro del `while True`.
- Eliminación de código duplicado que provocaba indentaciones inválidas.
- La función **siempre retorna lista** (`[]` en error) para evitar rupturas aguas abajo.

### Removed
- Bloques antiguos/duplicados de parsing y logs que generaban confusión e indentación incorrecta.

### Notes
- No hay breaking changes en la API pública del script.
- Requiere tener configuradas variables `ISPCUBE_BASE_URL`, `ISPCUBE_USERNAME`, `ISPCUBE_PASSWORD`, `ISPCUBE_API_KEY`, `ISPCUBE_CLIENT_ID` y opcional `ISPCUBE_LIMIT`.

## [1.2.0 - 2025-08-21
### Fixed
- Errores de `NameError` y `SyntaxError` al mover el parseo JSON dentro de la función y ordenar returns/logs.

## [1.1.1] - 2025-08-20
### Added
- Logs en nivel DEBUG y trazas de requests para diagnóstico.
- Ejemplo de captura de cabeceras y muestra de un registro de cliente.

## [1.0.0]
### Added
- Autenticación con `/sanctum/token` y uso de headers `api-key`, `client-id`, `login-type`, `username`.

## [1.0.0]
### Added
- Versión inicial del sincronizador ISPCube → Flowdat (estructura del proyecto y consultas básicas).
