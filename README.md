<h1 align="center">Juan Sebastián Pineda Santafé</h1>

<p align="center">
  <b>Estudiante de Ingeniería de Sistemas · Universidad El Bosque</b><br>
  Desarrollo backend y full-stack · Seguridad de la información · Sistemas embebidos
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Buscando-Práctica%20Profesional-2ea44f?style=for-the-badge" alt="Buscando práctica profesional">
</p>

<p align="center">
  <!-- Reemplaza TU_PERFIL y TU_CORREO con tus datos -->
  <a href="https://www.linkedin.com/in/TU_PERFIL"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  <a href="mailto:TU_CORREO@ejemplo.com"><img src="https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>
  <a href="https://github.com/Semiramyz"><img src="https://img.shields.io/badge/GitHub-Semiramyz-181717?style=flat-square&logo=github" alt="GitHub"></a>
</p>

---

## 👨‍💻 Sobre mí

Soy estudiante de Ingeniería de Sistemas y me enfoco en construir software **escalable, eficiente y bien organizado**. He trabajado en proyectos que van desde APIs REST con bases de datos relacionales y despliegue en contenedores, hasta un motor de juego nativo en C++ y aplicaciones con autenticación segura desplegadas en la nube con TLS.

- 🎯 **Busco:** práctica profesional en desarrollo backend, full-stack o seguridad.
- 🧠 **Me interesa:** arquitectura de software, sistemas embebidos, visión artificial, aviónica y sistemas médicos.
- 🛠️ **Cómo trabajo:** documento lo que construyo, separo responsabilidades por capas y busco que los proyectos se puedan levantar y probar fácilmente.

---

## 🚀 Proyectos destacados

### 🐝 [HoneyComb Engine — Plataforma NoCode 2.5D isométrica](https://github.com/Semiramyz/HoneyComb-Engine-Plataforma-de-desarrollo-NoCode-2.5D-Isometrico)
Prototipo de plataforma para crear experiencias interactivas isométricas de puzle y acción **sin escribir código**.
- **Editor de niveles** de escritorio con *drag & drop* sobre grilla isométrica y lógica por eventos, condiciones y acciones.
- **Motor de ejecución nativo** en C++17 sobre raylib con renderizado 2.5D, *Z-sorting* y colisiones.
- Arquitectura *data-driven*: editor y motor son independientes y se comunican mediante un **contrato JSON versionado** (`level.schema.json`), sin recompilar el motor al cambiar un nivel.

`C++17` `raylib` `Angular` `Electron` `TypeScript` `CMake` `vcpkg` `JSON Schema`

### 🛒 [Tienda DS — Sistema de gestión comercial](https://github.com/Semiramyz/Tienda_DS_MS)
Aplicación full-stack para administrar productos, clientes, proveedores, ventas, facturación y contabilidad.
- API REST en **ASP.NET Core 8** con arquitectura por capas (Controllers → Services → DbContexts) y DTOs.
- **Bases de datos separadas por dominio** (auth, clientes, productos, ventas, facturas, proveedores, contabilidad) con Entity Framework Core y MySQL.
- Autenticación con **JWT** y contraseñas con **BCrypt**; documentación de la API con Swagger.
- Entornos de desarrollo y producción con **Docker Compose** y pipeline de **GitHub Actions** que construye y publica las imágenes en GHCR.
- Evolución de una [versión monolítica inicial](https://github.com/Semiramyz/Tienda-DS).

`C#` `ASP.NET Core` `EF Core` `MySQL` `Angular` `JWT` `Docker` `GitHub Actions`

### 🔐 [Taller de Cifrado Clásico + Autenticación segura](https://github.com/Semiramyz/Taller-de-Cifrado-Clasico)
Aplicación web de criptoanálisis y módulo de inicio de sesión seguro, desplegada en la nube.
- **Criptoanálisis automático** de criptogramas César, Afín y Vigenère usando índice de coincidencia y frecuencias del español.
- Backend con **Express** y renderizado del lado del servidor (Angular SSR), hash de contraseñas con **bcrypt**, gestión de sesiones y **protección contra fuerza bruta**.
- Capa de datos intercambiable entre **MySQL y SQLite** mediante el patrón repositorio.
- Despliegue en **AWS EC2** con **nginx** como proxy inverso, comparando tres escenarios: sin SSL, certificado autofirmado y **Let's Encrypt** emitido y configurado manualmente.

`TypeScript` `Angular SSR` `Express` `bcrypt` `MySQL` `SQLite` `AWS EC2` `nginx` `TLS`

### 📐 [CreditRules DSL — Motor de reglas de crédito](https://github.com/Semiramyz/DSL-Lab)
Lenguaje de dominio específico para evaluar solicitudes de crédito sin reglas incrustadas en el código.
- Las reglas se representan como un **árbol de sintaxis abstracta (AST)** y se evalúan sobre un contexto de variables.
- Interfaz web con evaluación interactiva, casos de prueba, **visualización gráfica de los AST** y exportación a Graphviz (`.dot`).

`C#` `.NET` `AST` `Graphviz` `Diseño de lenguajes`

---

## 📂 Otros proyectos

| Proyecto | Descripción | Tecnologías |
| :--- | :--- | :--- |
| [Calculadora IP](https://github.com/Semiramyz/Redes-Maquina-Virtual-PIN) | Calcula red, broadcast, rango de hosts útiles, clase y tipo de IP, con representación binaria red/host. | PHP |
| [Ordenamiento de matrices](https://github.com/Semiramyz/ordenamiento_matrices) | Implementación y comparación de Bubble, Selection, Insertion, Merge y Quick Sort con arquitectura MVC e interfaz gráfica. | Java |
| Detección de personas con IA en ESP32 | Visión artificial ejecutada en un sistema embebido con interfaz web integrada. | C++, TensorFlow Lite, ESP32-CAM |

---

## 🧰 Tecnologías

**Lenguajes**

![C#](https://img.shields.io/badge/C%23-512BD4?style=flat-square&logo=dotnet&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=flat-square&logo=cplusplus&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![Java](https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Go](https://img.shields.io/badge/Go-00ADD8?style=flat-square&logo=go&logoColor=white)
![PHP](https://img.shields.io/badge/PHP-777BB4?style=flat-square&logo=php&logoColor=white)
![SQL](https://img.shields.io/badge/SQL%20%2F%20PL--SQL-4479A1?style=flat-square&logo=databricks&logoColor=white)

**Frameworks y librerías**

![.NET](https://img.shields.io/badge/ASP.NET%20Core-512BD4?style=flat-square&logo=dotnet&logoColor=white)
![Angular](https://img.shields.io/badge/Angular-DD0031?style=flat-square&logo=angular&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=nodedotjs&logoColor=white)
![Express](https://img.shields.io/badge/Express-000000?style=flat-square&logo=express&logoColor=white)
![Electron](https://img.shields.io/badge/Electron-47848F?style=flat-square&logo=electron&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring%20Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![raylib](https://img.shields.io/badge/raylib-000000?style=flat-square&logo=c&logoColor=white)
![TensorFlow Lite](https://img.shields.io/badge/TensorFlow%20Lite-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)

**Bases de datos**

![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![EF Core](https://img.shields.io/badge/Entity%20Framework%20Core-512BD4?style=flat-square&logo=dotnet&logoColor=white)

**DevOps, nube y herramientas**

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![AWS](https://img.shields.io/badge/AWS%20EC2-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white)
![nginx](https://img.shields.io/badge/nginx-009639?style=flat-square&logo=nginx&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)
![CMake](https://img.shields.io/badge/CMake-064F8C?style=flat-square&logo=cmake&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=flat-square&logo=swagger&logoColor=black)

---

## 🎓 Formación

**Ingeniería de Sistemas** — Universidad El Bosque, Colombia
<!-- Opcional: agrega el semestre actual, por ejemplo: "Octavo semestre · Graduación esperada 2027" -->

---

## 📫 Contacto

Estoy disponible para **práctica profesional**. Si mi perfil encaja con tu equipo, escríbeme:

- 💼 LinkedIn: [linkedin.com/in/TU_PERFIL](https://www.linkedin.com/in/TU_PERFIL)
- ✉️ Correo: [TU_CORREO@ejemplo.com](mailto:TU_CORREO@ejemplo.com)

<p align="center"><i>Gracias por visitar mi perfil.</i></p>
