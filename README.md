# Proyecto: Sistema de Rutinas de Gimnasio Personalizadas con IA y Soporte Médico - Backend

Este repositorio contiene el backend para el Sistema de Rutinas de Gimnasio Personalizadas. Está construido con Python y FastAPI.

## Descripción General

El backend gestiona:
- Autenticación de usuarios y médicos.
- Recopilación y almacenamiento de datos de usuarios (objetivos, experiencia) e información médica.
- Interacción con la API de Google Gemini para generar rutinas de entrenamiento personalizadas.
- Ensamblaje de rutinas con detalles de ejercicios (descripciones, URLs de medios, precauciones) desde la base de datos.
- Provisión de una API RESTful para las aplicaciones frontend (web y móvil).

## Pila Tecnológica (Backend)

- **Lenguaje**: Python 3.10+
- **Framework**: FastAPI
- **Servidor ASGI**: Uvicorn
- **Validación de Datos**: Pydantic
- **Base de Datos**: PostgreSQL (a través de Supabase)
- **IA**: Google Gemini API
- **Gestión de Entorno**: python-dotenv

## Configuración del Entorno

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_DIRECTORIO_DEL_PROYECTO>
    ```

2.  **Crear un entorno virtual:**
    (Se recomienda Python 3.10 o superior)
    ```bash
    python -m venv venv
    ```

3.  **Activar el entorno virtual:**
    - En macOS y Linux:
      ```bash
      source venv/bin/activate
      ```
    - En Windows:
      ```bash
      venv\Scripts\activate
      ```

4.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configurar variables de entorno:**
    - Copia el archivo `.env.example` a `.env`:
      ```bash
      cp .env.example .env
      ```
    - Edita el archivo `.env` y añade tus credenciales de Supabase y la API Key de Google Gemini:
      ```
      SUPABASE_URL="your_supabase_url_here"
      SUPABASE_KEY="your_supabase_anon_or_service_key_here"
      GEMINI_API_KEY="your_gemini_api_key_here"
      ```

## Ejecutar la Aplicación (Desarrollo Local)

Para iniciar el servidor de desarrollo local:

```bash
python app/main.py
```

O directamente con Uvicorn (más control sobre workers, reload, etc.):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`.
La documentación interactiva de la API (Swagger UI) estará en `http://localhost:8000/docs`.
La especificación OpenAPI estará en `http://localhost:8000/api/v1/openapi.json`.

## Estructura del Proyecto (Backend)

```
.
├── app/                  # Directorio principal de la aplicación FastAPI
│   ├── core/             # Configuración, lógica core
│   │   ├── config.py     # Carga de settings y variables de entorno
│   │   └── __init__.py
│   ├── main.py           # Punto de entrada de la aplicación FastAPI, incluye routers
│   ├── models/           # Modelos Pydantic (validación de datos, esquemas API)
│   │   ├── user.py
│   │   ├── exercise.py
│   │   ├── routine.py
│   │   └── __init__.py
│   ├── routers/          # Endpoints de la API
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── doctors.py
│   │   └── __init__.py
│   ├── services/         # Lógica de negocio, interacción con servicios externos
│   │   ├── prompt_service.py
│   │   ├── gemini_service.py
│   │   ├── routine_service.py
│   │   └── __init__.py
│   └── __init__.py
├── requirements.txt      # Dependencias de Python
├── .env.example          # Archivo de ejemplo para variables de entorno
└── README.md             # Este archivo
```

## Próximos Pasos y TODOs

-   [ ] Implementar la lógica real de interacción con Supabase (reemplazar mocks).
-   [ ] Implementar la lógica real de llamadas a la API de Gemini (reemplazar mocks).
-   [ ] Desarrollar tests unitarios e de integración.
-   [ ] Añadir manejo de errores más robusto.
-   [ ] Implementar autenticación y autorización completas con Supabase Auth.
-   [ ] Poblar la base de datos de ejercicios en Supabase.
-   [ ] Refinar los modelos Pydantic y la estructura de los prompts para Gemini.
