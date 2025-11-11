# 🌿 MiFlaskApp - SimpleFlaskHomework

Aplicación web desarrollada en **Flask (Python)** con conexión a **MongoDB**, que incluye autenticación con **JWT**, control de roles (`admin`, `manager`, `user`) y endpoints temáticos sobre **plantas** 🌱.

---

## 🚀 Funcionalidades principales

- 🔐 Login y registro de usuarios con **JWT**.  
- 👥 Roles definidos: `admin`, `manager`, `user`.  
- 🌱 CRUD básico de plantas (crear y listar).  
- 🔎 Filtro por nivel de cuidado (`care_level`).  
- 👤 Visualización de usuarios (solo roles autorizados).  
- 🌍 Página pública con lista de usuarios visibles.  
- 🧩 Conexión a **MongoDB** mediante variables de entorno (`.env`).  

---

## 🛠️ Requisitos

- Python 3.8 o superior  
- MongoDB (local o MongoDB Atlas)  
- Git  

---

## ⚙️ Instalación y ejecución

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/esperanzabm/HOMEWORK_SIMPLEFLASK.git
cd MiFlaskApp/SimpleFlaskHomework