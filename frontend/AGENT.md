# Frontend — TalentMatch (Angular 17)

Aplicación Angular 17 standalone (sin NgModules) que sirve como interfaz de usuario para la plataforma JobSearcher. Se ejecuta en el puerto **4200** (dev) / **8501** (expuesto vía Docker).

## Estructura del proyecto

```
frontend/
├── src/
│   ├── index.html              # Punto de entrada HTML (carga Google Fonts y Material Symbols)
│   ├── main.ts                 # Bootstrap de la aplicación (bootstrapApplication)
│   ├── styles.css              # Estilos globales (Tailwind base/components/utilities + custom)
│   └── app/
│       ├── app.config.ts       # Proveedores: Router + HttpClient (Fetch API)
│       ├── app.routes.ts       # Rutas: / → redirect a /dashboard
│       ├── app.component.ts    # Componente raíz (Navbar + Sidebar + RouterOutlet)
│       ├── pages/
│       │   ├── dashboard/      # Página principal — lista de ofertas, carga datos y filtros
│       │   └── sources/        # Gestión de fuentes de datos (JSearch, LinkedIn, SerpApi)
│       ├── components/
│       │   ├── navbar/         # Barra superior fija (brand, navegación, iconos)
│       │   ├── sidebar/        # Sidebar izquierdo (filtros: All Jobs / Applicable Jobs)
│       │   ├── job-card/       # Tarjeta de oferta individual (anillo de match, botones de acción)
│       │   └── job-detail-modal/ # Modal full-screen con detalle completo de la oferta
│       ├── services/
│       │   ├── job.service.ts      # API calls: GET /jobs, POST tailored-pdf, POST cover-letter
│       │   ├── filter-state.service.ts  # Estado reactivo (BehaviorSubject) para filtro applicable
│       │   └── source.service.ts   # Gestión de fuentes de extracción
│       └── models/
│           ├── job.model.ts        # Interfaz Job + datos mock de fallback
│           └── source.model.ts     # Interfaz para fuentes de datos
├── angular.json               # Configuración de Angular CLI (builder esbuild)
├── package.json               # Dependencias (Angular 17, Tailwind, RxJS) y scripts
├── tsconfig.json              # Configuración base de TypeScript
├── tailwind.config.js         # Configuración de Tailwind CSS
├── postcss.config.js          # Plugins de PostCSS
├── proxy.conf.json            # Proxy de desarrollo: /api/* → localhost:8000/*
└── Dockerfile                 # Imagen Docker multistage para producción
```

## Flujo de navegación

1. `/` redirige a `/dashboard`
2. Navbar siempre visible con brand "TalentMatch", enlaces y botones
3. Sidebar izquierdo alterna entre "All Jobs" y "Applicable Jobs" vía FilterStateService
4. Dashboard carga ofertas con JobService.getJobs() y las renderiza como JobCard[]
5. Click en card → abre JobDetailModal con acciones: Apply Now, Generate CV, Cover Letter

## Servicios

| Servicio | Propósito |
|---|---|
| `JobService` | Singleton. GET /jobs con filtros y paginación, POST para generación de PDFs. Fallback a datos mock si la API falla. |
| `FilterStateService` | Singleton. Maneja un BehaviorSubject con el estado del filtro applicable (undefined = all, true = only applicable). |
| `SourceService` | Singleton. CRUD de fuentes de extracción de datos. |

## Componentes clave

| Componente | Inputs | Outputs | Rol |
|---|---|---|---|
| `DashboardComponent` | — | — | Orquesta la carga de ofertas y la apertura del modal |
| `JobCardComponent` | `job: Job` | `viewDetails` | Muestra resumen de oferta + 3 botones de acción |
| `JobDetailModalComponent` | `job: Job` | `close` | Modal con info completa + botones de acción |
| `SidebarComponent` | — | — | Controla el filtro applicable |
| `NavbarComponent` | — | — | Barra de navegación superior |

## Configuración de desarrollo

- **Dev server:** `ng serve` en puerto 4200
- **Proxy:** `/api/*` → `http://localhost:8000/*` (proxy.conf.json)
- **Estilos:** Tailwind CSS + Google Fonts (Inter, JetBrains Mono) + Material Symbols Outlined
