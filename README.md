# 📈 Financial-SIP-Projection-API

## 🌟 Project Overview: SIP Projection Service

This project delivers a **RESTful API** for calculating and projecting the future value of Systematic Investment Plans (SIPs). Its primary function is to serve as a robust, clean, and transparent financial service that models compounding growth, allowing a client application to easily visualize and compare potential investment outcomes.

The architecture is split into two distinct, independently manageable components: the core Java **Calculation Service** and the Python **Client/Scripting Module**.

### Key Features
* **Core Calculation API:** A clean, high-performance RESTful endpoint (built with Spring Boot) for the precise mathematical calculation of SIP Future Value.
* **Asset Comparison Logic:** Built-in logic to allow comparison against alternative assets (like Fixed Deposits) based on the same input parameters.
* **Modular Architecture:** Adheres to **Single Responsibility Principle** (SRP) where the backend is purely a calculation microservice, and the Python component handles data presentation.
* **Visualization Ready Output:** API responses are structured in JSON for immediate consumption by any modern charting library (Chart.js, D3, etc.).

### Technology Stack
| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend** | Java, Spring Boot, Maven | RESTful API and Core Business Logic |
| **Client/Scripts** | Python | Initial data handling, API testing, and basic visualization examples |

---

## 🚀 Getting Started

This project requires setting up two separate environments: the Backend (Java/Spring Boot) and the Client/Scripting (Python).

### Prerequisites

* **Java Development Kit (JDK) 17 or higher**
* **Maven 3.8+**
* **Python 3.9 or higher**
* **Git**

### Project Structure

| Folder | Technology | Purpose |
| :--- | :--- | :--- |
| `IntelliJ-SIP-Backend` | Java (Spring Boot) | **API Service.** Contains the `@RestController`, business service, and calculation DTOs. |
| `PyCharm-SIP-Frontend` | Python | **Client Logic.** Contains Python scripts to demonstrate calling the API and consuming the JSON response. |

---

## 🛠️ Installation & Setup

### 1. Backend API (Java/Spring Boot)

1.  **Navigate** to the backend directory:
    ```bash
    cd IntelliJ-SIP-Backend
    ```
2.  **Build the project** using Maven:
    ```bash
    mvn clean install
    ```
3.  **Run the application** (e.g., using the Spring Boot Maven plugin):
    ```bash
    mvn spring-boot:run
    ```
4.  The API will start on `http://localhost:8080`.

### 2. Client/Scripts (Python)

1.  **Navigate** to the Python directory:
    ```bash
    cd PyCharm-SIP-Frontend
    ```
2.  **Install dependencies** (e.g., `requests` for API calls, `matplotlib` for charts):
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the client script** to test the API (replace `api_client.py` with your entry file):
    ```bash
    python3 api_client.py
    ```

---

## 💻 API Endpoints

The API follows **RESTful conventions** (using nouns and HTTP verbs) and returns standard JSON responses.

### Core Calculation Endpoint

| Method | Resource | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/projection/sip` | Calculates the projected future value and total invested amount. |

**Example Request Body (`POST` to `/api/v1/projection/sip`):**

```json
{
  "monthlyInvestment": 10000.0,
  "years": 20,
  "expectedAnnualRate": 0.12
}
