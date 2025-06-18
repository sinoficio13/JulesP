from fastapi import FastAPI # Asegurarse de que Depends esté importado si se usa a nivel de app o router. Depends ya no es necesario aquí.
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, users, doctors
# from app.core.auth_deps import bearer_auth_scheme # No es necesario importar bearer_auth_scheme aquí directamente

# Definición del esquema de seguridad para OpenAPI (esto es lo que Swagger UI usará)
# El nombre "BearerAuth" es un identificador que usaremos en la sección 'security' de los routers/endpoints.
OPENAPI_COMPONENTS = {
    "securitySchemes": {
        "BearerAuth": {
            "type": "apiKey", # Para tokens Bearer, 'apiKey' en 'header' es una forma común de representarlo
                              # Alternativamente, se podría usar 'http' con scheme 'bearer'.
                              # 'apiKey' suele dar la UI más simple en Swagger para pegar un token.
            "name": "Authorization", # El nombre del header
            "in": "header",          # Dónde se encuentra la "API key" (en este caso, el token)
            "description": "Enter your JWT token prefixed with 'Bearer '. Example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c. **The 'Bearer ' prefix (with a space) is required.**"
        }
        # Podríamos también definir el oauth2_scheme aquí si quisiéramos que apareciera
        # explícitamente como una opción separada en la documentación, pero para simplificar
        # el diálogo "Authorize" de Swagger UI, nos enfocaremos en "BearerAuth".
        # "OAuth2PasswordBearer": {
        #     "type": "oauth2",
        #     "flows": {
        #         "password": {
        #             "tokenUrl": f"{settings.API_V1_STR}/auth/login", # Tomado de oauth2_scheme
        #             "scopes": {} # No estamos usando scopes actualmente
        #         }
        #     }
        # }
    }
}

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    components=OPENAPI_COMPONENTS # Añadir los componentes de seguridad a OpenAPI
)

# --- CORS Configuration ---
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    # "https://your-frontend-domain.com", # TODO: Add your production frontend domain here
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- End CORS Configuration ---

# El router de autenticación NO lleva el `security` global, sus endpoints son públicos.
app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["Authentication"])

# Aplicar el esquema de seguridad "BearerAuth" a los routers que contienen endpoints protegidos.
# La lista vacía `[]` para scopes significa que no se usan scopes de OAuth2 específicos.
# SECURITY_PARAMS_BEARER_AUTH = [{"BearerAuth": []}] # No se usa directamente en include_router

# Re-escribiendo la inclusión de routers para ser más explícitos con el parámetro `security`
# para OpenAPI, en lugar de solo `dependencies` para la ejecución.

# Limpiar `dependencies` de los routers si solo queremos que `security` maneje la parte de OpenAPI
# y las dependencias individuales en cada ruta manejen la ejecución.
# O, mantener `Depends(bearer_auth_scheme)` a nivel de router si queremos que *todas* las rutas
# de ese router estén protegidas por defecto por ese esquema (lo cual es razonable).
# La dependencia `get_current_authenticated_user` ya usa `Depends(bearer_auth_scheme)`.

# Para que Swagger UI muestre el candado en los endpoints de estos routers y
# sepa que usan "BearerAuth", podemos añadir `security` a `include_router`.
# No es estrictamente necesario si las dependencias en las rutas ya usan `bearer_auth_scheme`,
# pero puede hacer la especificación OpenAPI más explícita.

# Vamos a quitar `dependencies=[Depends(bearer_auth_scheme)]` de `include_router`
# y confiar en que las dependencias individuales (`Depends(get_current_authenticated_user)`)
# que ya usan `bearer_auth_scheme` informarán a OpenAPI.
# El cambio principal es la definición de `OPENAPI_COMPONENTS`.

app.include_router(
    users.router,
    prefix=settings.API_V1_STR + "/users",
    tags=["Users"]
    # No es necesario `security=SECURITY_PARAMS_BEARER_AUTH` aquí si las rutas individuales
    # ya están protegidas con `Depends(get_current_authenticated_user)` que usa `bearer_auth_scheme`.
    # FastAPI es suficientemente inteligente. El `components` que definimos arriba es la clave.
)

app.include_router(
    doctors.router,
    prefix=settings.API_V1_STR + "/doctors",
    tags=["Doctors"]
    # Idem para `security` aquí.
)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}. Visit /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
