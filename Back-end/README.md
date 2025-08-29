# README: Backend (FastAPI)

Este repositorio contiene el backend del sistema de sorteos, desarrollado con **FastAPI (Python)**. El sistema optimiza la ejecución y grabación de sorteos periódicos, permitiendo la precarga de sorteos para reducir el tiempo de preparación en grabaciones o transmisiones en vivo. Está diseñado para entornos tanto virtuales como presenciales, lo que facilita su uso para operadores técnicos y usuarios con mínima experiencia.

Este proyecto fue desarrollado de manera independiente por Christian Hoyos Salazar para la empresa Gane Super Giros.

---

## 🎯 Funcionalidades Principales

El backend gestiona toda la **lógica de negocio**, incluyendo:

* **Gestión** de participantes y sorteos.
* **Ejecución** de sorteos y almacenamiento de resultados.
* **Integración** con una base de datos **MySQL** para la persistencia de datos.

---

## 🛠️ Requisitos

* **Python:** 3.8 o superior
* **FastAPI**
* **MySQL Server:** Debe estar instalado y en ejecución (por ejemplo, a través de XAMPP).

---

## 🚀 Instalación

1.  **Instala FastAPI y Uvicorn:** Se recomienda hacerlo en un entorno virtual.
    ```sh
    pip install fastapi uvicorn
    ```
2.  **Instala el conector de MySQL:**
    ```sh
    pip install mysql-connector-python
    ```
3.  **Asegúrate de que el servidor MySQL esté corriendo** (p.ej., a través de XAMPP).
4.  **Ejecuta el backend:** Desde el directorio que contiene `main.py`, ejecuta el siguiente comando:
    ```sh
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
    ```
    La API estará disponible en [http://localhost:8001/](http://localhost:8001/).

---

## 🔗 Conexión con Frontend y Base de Datos

* El frontend consume esta API en el **puerto 8001**.
* La conectividad a la base de datos **MySQL** se gestiona a través de consultas SQL directas o un ORM (Object-Relational Mapper).

---

## 💡 Consideraciones Adicionales

* Es una **API RESTful de alto rendimiento** con validaciones automáticas.
* Está integrado con un frontend desarrollado en **Angular** y una base de datos **MySQL**.
* Diseñado para un **uso continuo** en sesiones de grabación o transmisión.