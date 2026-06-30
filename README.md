# CaribeanOcean Analytics

## Ejecutar API

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.infrastructure.main:app --reload
```

Documentacion interactiva:

```text
http://127.0.0.1:8000/docs
```

## Prediccion de ocupacion

El proyecto expone un modelo de prediccion de ocupacion hotelera basado en ocupacion
diaria historica, patron semanal y tendencia reciente.

Endpoint para el dashboard:

```text
GET /api/v1/occupancy/dashboard?date_from=2026-01-01&date_to=2026-06-30&forecast_days=30
```

Endpoint directo del modelo:

```text
GET /api/v1/occupancy/forecast?date_from=2026-01-01&date_to=2026-06-30&forecast_days=30
```

Ambos devuelven historico diario, prediccion diaria, ocupacion promedio predicha,
fecha pico predicha y confianza del pronostico.
