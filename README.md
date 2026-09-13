<div align="center">

# 🌿 RouteZero
### Optimizador de Rutas Sostenibles para Flotas de Reparto

[![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow?style=for-the-badge)]()
[![Versión](https://img.shields.io/badge/Versión-v1.0.0-blue?style=for-the-badge)]()
[![Licencia](https://img.shields.io/badge/Licencia-MIT-green?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)]()
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql)]()

**Taller de Proyectos 2 — Ingeniería de Sistemas e Informática**
**Universidad Continental | Huancayo, Perú | 2026**

</div>

---

## 📋 Tabla de Contenido

- [Sobre el Proyecto](#-sobre-el-proyecto)
- [Problemática](#-problemática)
- [Solución](#-solución)
- [Justificación del MVP](#-justificación-del-mvp)
- [Objetivos](#-objetivos)
- [Stack Tecnológico](#-stack-tecnológico)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Equipo de Desarrollo](#-equipo-de-desarrollo)
- [Estándares Aplicados](#-estándares-aplicados)
- [Enfoque de Desarrollo](#-enfoque-de-desarrollo)
- [Estructura del Repositorio](#-estructura-del-repositorio)
- [Documentación](#-documentación)
- [Instalación](#-instalación)

---

## 🌿 Sobre el Proyecto

**RouteZero** es una plataforma web de optimización de rutas logísticas sostenibles desarrollada como Proyecto Final de Asignatura (PFA) del curso Taller de Proyectos 2 de la carrera de Ingeniería de Sistemas e Informática de la Universidad Continental.

El sistema está diseñado para **Andina Reparto S.A.C.**, empresa ficticia de distribución logística con sede en el **Parque Industrial de El Tambo, Huancayo**, que realiza entregas diarias a bodegas, mercados y pequeños comerciantes del distrito de Huancayo, Junín.

RouteZero aplica algoritmos metaheurísticos para resolver el **Problema de Ruteo de Vehículos con Ventanas de Tiempo (VRPTW)** con variante ecológica **(Green VRP)**, optimizando simultáneamente la distancia recorrida, el consumo de combustible, las emisiones de CO₂ y el cumplimiento de horarios de entrega.

---

## 🚨 Problemática

Andina Reparto S.A.C. enfrenta cuatro desafíos operativos críticos en su operación diaria dentro del distrito de Huancayo:

### 1. Alta congestión vehicular
Las principales vías del distrito presentan congestión severa en horas punta:
- **Horas punta**: 7:30–9:30 | 12:00–14:30 | 17:00–21:00
- **Vías críticas**: Av. Ferrocarril (hasta 3,186 vehículos/hora), Av. Giráldez y Calle Real
- La Av. Ferrocarril, desde el puente Los Andes hasta el Jr. Tarapacá, puede generar esperas de hasta **1 hora** en hora punta

### 2. Altos costos operativos
- El combustible y mantenimiento de la flota representan una parte significativa de los costos totales
- La planificación manual de rutas genera recorridos ineficientes y tiempos muertos

### 3. Impacto ambiental
- La flota genera emisiones de CO₂ evitables mediante una planificación inteligente de rutas
- Ausencia de métricas de sostenibilidad y planes de compensación de carbono

### 4. Incumplimiento de ventanas de tiempo
- Un porcentaje significativo de entregas se realiza fuera del horario acordado
- Genera penalidades económicas y pérdida de clientes

---

## 💡 Solución

RouteZero resuelve estos problemas mediante una plataforma web moderna que:

- 🗺️ **Calcula rutas óptimas** aplicando metaheurísticas (Algoritmo Genético + VRPTW + Green VRP)
- ⚡ **Genera soluciones en ≤ 45 segundos** para hasta 150 pedidos y 15 vehículos
- 📍 **Visualiza rutas** en mapa interactivo con Leaflet + OpenStreetMap
- 📊 **Monitorea en tiempo real** métricas de CO₂, combustible y cumplimiento de entregas
- 📄 **Genera reportes PDF** de sostenibilidad e impacto ambiental
- 🔄 **Re-optimiza dinámicamente** ante cancelaciones, nuevos pedidos o incidentes de tráfico
- 🌱 **Propone planes de compensación de carbono** alineados a objetivos de cero carbono neto

---

## 🎯 Justificación del MVP

El MVP de RouteZero se justifica por la necesidad de demostrar en un entorno académico controlado que la aplicación de algoritmos metaheurísticos a la logística urbana de Huancayo genera un impacto medible en la eficiencia operativa y la sostenibilidad ambiental. La plataforma web permite validar el modelo de optimización con datos reales de la geografía y el tráfico del distrito de Huancayo, estableciendo una base escalable para futuras versiones del sistema.

---

## 🎯 Objetivos

### Objetivo General
Desarrollar una plataforma web funcional que optimice las rutas de reparto de Andina Reparto S.A.C. en el distrito de Huancayo, minimizando distancia, consumo de combustible, emisiones de CO₂ y penalizaciones por incumplimiento de ventanas de tiempo.

### Objetivos Específicos
- Implementar un algoritmo metaheurístico (VRPTW + Green VRP) en Python con tiempo de respuesta ≤ 45 segundos
- Desarrollar una interfaz web intuitiva con React.js que incluya visualización de rutas en mapa interactivo
- Construir una API REST con FastAPI que gestione flota, pedidos, conductores y rutas
- Generar reportes de sostenibilidad con métricas reales de CO₂ y costos operativos
- Cumplir con los estándares W3C, ISO/IEC 25010, OWASP Top 10, WCAG 2.1 y Green Software

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Versión | Justificación |
|---|---|---|---|
| **Frontend** | React.js | 18+ | Ecosistema amplio, integración nativa con Leaflet, componentes reutilizables |
| **Backend** | Python + FastAPI | 3.11+ / 0.100+ | Ideal para APIs REST, genera Swagger automáticamente, perfecto para algoritmos en Python |
| **Base de datos** | PostgreSQL | 15+ | Robusto, open source, soporte para datos geoespaciales |
| **Mapas** | Leaflet + OpenStreetMap | — | Gratuito, sin límites de uso, datos precisos para Huancayo |
| **Algoritmo** | Python (metaheurísticas) | — | VRPTW + Green VRP implementado en Python puro |
| **Control de versiones** | Git + GitHub | — | Flujo Feature Branch Workflow con versionado semántico |
| **Documentación API** | Swagger / OpenAPI | — | Generado automáticamente por FastAPI |

---

## 🏗️ Arquitectura del Sistema

> La arquitectura detallada se encuentra en [`docs/01 Inicio/`](docs/01%20Inicio/)

El sistema sigue una arquitectura de **tres capas** con separación clara de responsabilidades:
```
Frontend (React.js)
      ↕ HTTP / REST API
Backend (Python + FastAPI)
      ↕ ORM / SQL
Base de datos (PostgreSQL)
```

**Componentes principales:**
- **Motor de optimización**: algoritmo metaheurístico VRPTW + Green VRP
- **API REST**: endpoints para gestión de flota, pedidos, rutas y reportes
- **Interfaz web**: dashboard, mapa interactivo y módulos de gestión
- **Motor de reportes**: generación de PDFs con métricas de sostenibilidad

---

## 👥 Equipo de Desarrollo

| Rol | Integrante |
|---|---|
| 🏛️ **Arquitecta de Software** | Inciso Aguilar Elizabeth Antonela |
| 🤖 **Ingeniero de IA e Integración** | Espinoza Tiza Yago Imanol |
| ⚙️ **Desarrollador Backend** | Guerra Lozano Keen |
| 🎨 **Desarrollador Frontend** | Uscuvilca Ramos Abraham Luis |

**Universidad Continental — Ingeniería de Sistemas e Informática**
**Taller de Proyectos 2 | Huancayo, Perú | 2026**

---

## 📐 Estándares Aplicados

| Estándar | Aplicación |
|---|---|
| **W3C** | Validación de HTML, CSS y JavaScript |
| **ISO/IEC 25010** | Evaluación de calidad del software en 8 características |
| **OWASP Top 10** | Mitigación de vulnerabilidades web críticas |
| **WCAG 2.1 AA** | Accesibilidad web para todos los usuarios |
| **Green Software** | Diseño energéticamente eficiente |
| **ISO 14083** | Medición y reporte de huella de carbono logística |
| **Ley N° 29733** | Protección de Datos Personales del Perú |
| **DS 033-2012-MTC** | Restricción vehicular según último dígito de placa |

---

## 🔄 Enfoque de Desarrollo

RouteZero aplica un **enfoque híbrido adaptativo-dominante** (promedio de evaluación: **3.6/5**) que combina:

**Componente adaptativo — Scrum-Kanban**
- 4 iteraciones con entregables parciales (semanas 1–14)
- Backlog de historias de usuario por épicas funcionales
- Tablero Kanban con límite WIP

**Componente predictivo — PMBOK 7ª Edición**
- Acta de constitución y documentación formal por fase
- Diagrama de Gantt para seguimiento del cronograma
- Matriz de riesgos con probabilidad e impacto

---

## 📁 Estructura del Repositorio
```
RouteZero/
├── docs/
│   ├── 01 Inicio/
│   │   ├── 01. Selección del enfoque del proyecto V_1_0_0.md
│   │   ├── 02. Acta de constitución V_1_0_0.md
│   │   ├── 03. Declaración de la visión V_1_0_0.md
│   │   ├── 04. Registro de supuestos y restricciones V_1_0_0.md
│   │   └── 05. Registro de interesados V_1_0_0.md
│   ├── 02 Planificacion/
│   ├── 03 Ejecucion/
│   ├── 04 Seguimiento_Control/
│   └── 05 Cierre/
├── backend/
│   └── tests/
├── frontend/
│   └── tests/
├── otros/
├── .env.example
├── .gitignore
└── README.md
```

---

## 📚 Documentación

### Fase 01: Inicio

| Documento | Ubicación |
|---|---|
| Selección del enfoque del proyecto | [`docs/01 Inicio/01. Selección del enfoque del proyecto V_1_1_0.md`](docs/01%20Inicio/01.%20Selección%20del%20enfoque%20del%20proyecto%20V_1_1_0.md) |
| Acta de constitución | [`docs/01 Inicio/02. Acta de constitución V_1_0_0.md`](docs/01%20Inicio/02.%20Acta%20de%20constitución%20V_1_0_0.md) |
| Declaración de la visión | [`docs/01 Inicio/03. Declaración de la visión V_1_0_0.md`](docs/01%20Inicio/03.%20Declaración%20de%20la%20visión%20V_1_0_0.md) |
| Registro de supuestos y restricciones | [`docs/01 Inicio/04. Registro de supuestos y restricciones V_1_0_0.md`](docs/01%20Inicio/04.%20Registro%20de%20supuestos%20y%20restricciones%20V_1_0_0.md) |
| Registro de interesados | [`docs/01 Inicio/05. Registro de interesados V_1_0_0.md`](docs/01%20Inicio/05.%20Registro%20de%20interesados%20V_1_0_0.md) |
| Requisitos funcionales | [`docs/01 Inicio/06. Requisitos funcionales V_1_0_0.md`](docs/01%20Inicio/06.%20Requisitos%20funcionales%20V_1_0_0.md) |
| Requisitos no funcionales | [`docs/01 Inicio/07. Requisitos no funcionales V_1_0_0.md`](docs/01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md) |
| Usuarios | [`docs/01 Inicio/08. Usuarios V_1_0_0.md`](docs/01%20Inicio/08.%20Usuarios%20V_1_0_0.md) |
| Reglas de negocio | [`docs/01 Inicio/09. Reglas de negocio V_1_0_0.md`](docs/01%20Inicio/09.%20Reglas%20de%20negocio%20V_1_0_0.md) |
| Stack tecnológico | [`docs/01 Inicio/10. Stack tecnológico V_1_0_0.md`](docs/01%20Inicio/10.%20Stack%20tecnológico%20V_1_0_0.md) |
| Base de datos | [`docs/01 Inicio/11. Base de datos V_1_0_0.md`](docs/01%20Inicio/11.%20Base%20de%20datos%20V_1_0_0.md) |
| Modelo C4 | [`docs/01 Inicio/12. Modelo C4 V_1_0_0.md`](docs/01%20Inicio/12.%20Modelo%20C4%20V_1_0_0.md) |
| Restricciones | [`docs/01 Inicio/13. Restricciones V_1_0_0.md`](docs/01%20Inicio/13.%20Restricciones%20V_1_0_0.md) |

---

### Fase 02: Planificación del Proyecto

| Documento | Ubicación |
|---|---|
| Transformando a Ágil | [`docs/02 Planificación/01 Transformando a ágil V_1_0_0.md`](docs/02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_0.md) |
| Artefactos Jira | [`docs/02 Planificación/02 Artefactos Jira V_1_0_0.md`](docs/02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md) |
| Registro de Riesgos | [`docs/02 Planificación/03 Registro de riesgos V_1_0_0.md`](docs/02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md) |
| Presupuesto del Proyecto | [`docs/02 Planificación/04 Presupuesto del proyecto V_1_0_0.md`](docs/02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md) |

---

<div align="center">

**RouteZero** — Optimizando rutas, reduciendo huella 🌿

*Universidad Continental | Ingeniería de Sistemas e Informática | 2026*

</div>
