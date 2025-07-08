# 🚀 HDD Data Analysis - Inicio Rápido con Docker

## ⚡ Ejecución en 3 Pasos

### 1. Preparar el Entorno

```bash
# Clonar o descargar el proyecto
cd hdd_data_analysis

# Copiar configuración de ejemplo
cp env.example .env

# Editar configuración de base de datos (opcional)
# Si usas los valores por defecto, no necesitas editar .env
```

### 2. Construir la Imagen

**Windows:**
```cmd
scripts\docker-run.bat build
```

**Linux/Mac:**
```bash
chmod +x scripts/docker-run.sh
./scripts/docker-run.sh build
```

### 3. Ejecutar Análisis

**Una sola vez:**
```bash
# Windows
scripts\docker-run.bat once

# Linux/Mac
./scripts/docker-run.sh once
```

**Programado (cada 24 horas):**
```bash
# Windows
scripts\docker-run.bat scheduled

# Linux/Mac
./scripts/docker-run.sh scheduled
```

## 📋 Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `scripts/docker-run.sh once` | Ejecutar análisis una vez |
| `scripts/docker-run.sh scheduled` | Ejecutar programado |
| `scripts/docker-run.sh logs` | Ver logs en tiempo real |
| `scripts/docker-run.sh stop` | Detener contenedor |
| `scripts/docker-run.sh build` | Reconstruir imagen |

## 🔍 Verificar Resultados

Los resultados se guardan en la tabla `nv_hdd_an_resultados` de la base de datos.

### Consulta SQL para ver resultados:

```sql
SELECT TOP 10 * FROM nv_hdd_an_resultados 
ORDER BY fecha_ejecucion_del_codigo DESC
```

## 📊 Logs

Los logs se guardan en:
- `logs/hdd_data_analysis_YYYYMMDD.log` - Logs de la aplicación
- Contenedor Docker - Logs del sistema

### Ver logs en tiempo real:
```bash
# Windows
scripts\docker-run.bat logs

# Linux/Mac
./scripts/docker-run.sh logs
```

## ⚠️ Solución de Problemas Rápidos

### Error de conexión a BD:
- Verificar que la BD esté accesible
- Revisar credenciales en `.env`

### Error de permisos:
```bash
mkdir -p logs
chmod 755 logs  # Solo Linux/Mac
```

### Contenedor no inicia:
```bash
docker logs hdd-data-analysis-run
```

## 📞 ¿Necesitas Ayuda?

1. Revisar `DOCKER_README.md` para documentación completa
2. Verificar logs de la aplicación
3. Contactar al equipo de desarrollo 