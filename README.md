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
      SUPABASE_KEY="your_supabase_anon_or_service_key_here" # Para operaciones básicas. Algunas funciones administrativas (ej. `supabase.auth.admin...`) pueden requerir la `service_role` key.
      GEMINI_API_KEY="your_gemini_api_key_here"
      ```

## Prerrequisitos de Base de Datos (Supabase)

Antes de ejecutar la aplicación y probar todas las funcionalidades, asegúrate de que las siguientes tablas existen en tu proyecto de Supabase:

1.  **`auth.users`**: Creada automáticamente por Supabase Auth.

2.  **`user_profiles`**:
    *   `user_id` (UUID, Primary Key, Foreign Key a `auth.users.id`)
    *   `objectives` (TEXT[]) - Array de strings
    *   `experience_level` (TEXT)
    *   `preferences` (JSONB)
    *   `email` (TEXT, Opcional) - Puede ser útil para denormalizar o evitar uniones en algunos casos.
    *   `created_at` (TIMESTAMPTZ, default `now()`)
    *   `updated_at` (TIMESTAMPTZ, default `now()`)

3.  **`medical_records`**:
    *   `medical_record_id` (UUID, Primary Key, default `gen_random_uuid()`)
    *   `user_id` (UUID, Foreign Key a `auth.users.id`)
    *   `doctor_id` (UUID) - Identificador del médico. Podría ser FK a `auth.users.id` si los médicos son usuarios, o a una tabla `doctors`.
    *   `conditions` (TEXT[])
    *   `limitations` (TEXT[])
    *   `recommendations` (TEXT)
    *   `created_at` (TIMESTAMPTZ, default `now()`)
    *   `updated_at` (TIMESTAMPTZ, default `now()`)

4.  **`exercises`**:
    *   `exercise_id` (UUID, Primary Key, default `gen_random_uuid()`)
    *   `name` (TEXT, UNIQUE, NOT NULL)
    *   `description` (TEXT)
    *   `muscles_targeted` (TEXT[])
    *   `equipment_needed` (TEXT[])
    *   `precautions` (TEXT)
    *   `image_url` (TEXT) - Debería ser una URL válida.
    *   `video_url` (TEXT) - Debería ser una URL válida.
    *   `created_at` (TIMESTAMPTZ, default `now()`)
    *   `updated_at` (TIMESTAMPTZ, default `now()`)

    **Importante**: Puebla la tabla `exercises` con algunos datos de ejemplo para que la generación de rutinas funcione correctamente.

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

## Autenticación

La API utiliza autenticación basada en tokens JWT proporcionados por Supabase.
Después de registrarse o iniciar sesión a través de los endpoints `/api/v1/auth/register` o `/api/v1/auth/login`, recibirás un `access_token`.

Para acceder a los endpoints protegidos, incluye este token en el header `Authorization` de tus peticiones:

```
Authorization: Bearer <TU_ACCESS_TOKEN_DE_SUPABASE>
```

La interfaz de `/docs` (Swagger UI) tiene un botón "Authorize" en la parte superior derecha donde puedes ingresar el token (incluyendo `Bearer `) para probar los endpoints protegidos directamente desde la documentación.

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

-   [ ] Implementar la lógica real de llamadas a la API de Gemini (reemplazar mocks en `GeminiService`).
-   [X] **Integración con Supabase (Datos)**:
    -   [X] Cliente Supabase configurado.
    -   [X] Autenticación integrada con Supabase Auth.
    -   [X] Servicios de perfiles de usuario (`user_profiles`) integrados.
    -   [X] Servicios de información médica (`medical_records`) integrados.
    -   [X] Base de datos de ejercicios (`exercises`) integrada con los servicios.
    -   [X] Servicios refactorizados para usar datos de Supabase en la preparación de prompts.
-   [X] **Autenticación JWT**: Implementado un sistema de dependencias para validar JWT de Supabase y proteger endpoints.
-   [ ] **Refinar Autorización**:
    -   Implementar lógica para asegurar que solo los médicos puedan añadir/modificar información médica.
    -   Asegurar que los usuarios solo puedan acceder/modificar sus propios datos (ej. perfil, solicitar rutina).
    -   Actualizar todos los endpoints que toman `user_id` o `doctor_id` del path para usar el ID del token autenticado (ej. `/users/me/profile` en lugar de `/users/{user_id}/profile`).
-   [ ] **Poblar la Base de Datos de Ejercicios**: Añadir un conjunto inicial y diverso de ejercicios en Supabase.
-   [ ] Desarrollar tests unitarios e de integración.
-   [ ] Añadir manejo de errores más robusto y validaciones detalladas.
-   [ ] Configurar Row Level Security (RLS) en Supabase para una capa adicional de seguridad de datos.
-   [ ] Considerar la paginación para endpoints que devuelven listas (ej. ejercicios, historial de rutinas).
-   [ ] Implementar endpoints para gestionar la tabla `doctors` si es necesario (crear perfiles de doctor, etc.).
