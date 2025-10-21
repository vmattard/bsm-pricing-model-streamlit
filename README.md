# Black-Scholes-Merton Pricing Model

An interactive **Streamlit app** for pricing European-style options using the **Black-Scholes-Merton (BSM)** model, with an **Option Chain viewer** powered by Yahoo Finance data.

---

## 🧩 Local Setup

```bash
# Clone the repository
git clone <your-repository-url>
cd <your-repository-directory>

# Create virtual environment
python -m venv .venv

# Activate it
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

Then open your browser to:

👉 [http://localhost:8501](http://localhost:8501)

---

## 🐳 Run with Docker Compose

You can also run the app using **Docker Compose** for a fully isolated environment.

### 1. Build and Run

```bash
docker compose up --build
```

This command will:
- Build the Docker image using the included `Dockerfile`.
- Start the Streamlit app in a container.

### 2. Access the App

Once running, open your browser and go to:

👉 [http://localhost:8501](http://localhost:8501)

### 3. Stop the Containers

To stop and remove the containers, press **Ctrl + C** or run:

```bash
docker compose down
```

---

💡 You should now see the Black-Scholes-Merton Option Pricing and Option Chain viewer running locally or in Docker!
