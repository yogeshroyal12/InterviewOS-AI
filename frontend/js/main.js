const API_BASE_URL = "http://127.0.0.1:8000";

async function checkBackendHealth() {
  const statusElement = document.getElementById("status");
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    statusElement.textContent = `${data.status} (${data.service})`;
  } catch (error) {
    statusElement.textContent = `unreachable: ${error.message}`;
  }
}

checkBackendHealth();