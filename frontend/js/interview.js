const API = "http://127.0.0.1:8000";
let token = null;
let interviewId = null;

const $ = (id) => document.getElementById(id);

async function login(email, password) {
  const res = await fetch(`${API}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(`Login failed (${res.status})`);
  token = (await res.json()).access_token;
}

async function startInterview(jobId, resumeId) {
  const res = await fetch(`${API}/api/v1/interviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ job_document_id: jobId, resume_document_id: resumeId }),
  });
  if (!res.ok) throw new Error(`Start failed (${res.status})`);
  const data = await res.json();
  interviewId = data.id;
  showQuestion(data.current_question);
}

function showQuestion(text, followUp = false) {
  if (!text) {
    $("question").textContent = "Interview complete.";
    $("status").textContent = "Finished. Loading your report...";
    loadReport();
    return;
  }
  $("question").textContent = text;
  $("status").textContent = followUp
    ? "Follow-up: please expand on your answer."
    : "Question ready. Click 'Read question aloud'.";
}

async function loadReport() {
  const res = await fetch(`${API}/api/v1/interviews/${interviewId}/report`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    $("status").textContent = `Report failed (${res.status}).`;
    return;
  }
  const r = await res.json();
  const items = r.items
    .map((i, n) => `<li><strong>Q${n + 1}</strong> score ${i.overall}/5<br>${i.evidence.join("<br>")}</li>`)
    .join("");
  $("status").innerHTML =
    `<strong>Overall score: ${r.overall_score}</strong><p>${r.limitations}</p><ol>${items}</ol>`;
}

function speak(text) {
  if (!("speechSynthesis" in window)) {
    $("status").textContent = "Speech output not supported in this browser.";
    return;
  }
  speechSynthesis.cancel();
  speechSynthesis.speak(new SpeechSynthesisUtterance(text));
}

function listen() {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) {
    $("status").textContent = "Speech input not supported. Please type your answer.";
    return;
  }
  const recognizer = new Recognition();
  recognizer.lang = "en-IN";
  recognizer.interimResults = false;
  $("status").textContent = "Listening...";
  recognizer.onresult = (event) => {
    $("answer").value = event.results[0][0].transcript;
    $("status").textContent = "Transcribed. Check the text, then submit.";
  };
  recognizer.onerror = (event) => {
    $("status").textContent = `Speech error: ${event.error}. Type your answer instead.`;
  };
  recognizer.start();
}

async function submitAnswer() {
  const answer = $("answer").value.trim();
  if (!answer) {
    $("status").textContent = "Please give an answer first.";
    return;
  }
  const res = await fetch(`${API}/api/v1/interviews/${interviewId}/answers`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ answer }),
  });
  if (!res.ok) {
    $("status").textContent = `Submit failed (${res.status}).`;
    return;
  }
  $("answer").value = "";
  const data = await res.json();
  showQuestion(data.current_question, data.follow_ups_used > 0);}

$("speak").onclick = () => speak($("question").textContent);
$("listen").onclick = listen;
$("submit").onclick = submitAnswer;

$("status").textContent = "Logging in...";
login("bobby@example.com", "secret123")
  .then(() => {
    $("status").textContent = "Starting interview (about 5 seconds)...";
    return startInterview(2, 1);
  })
  .catch((err) => {
    $("status").textContent = "Error: " + err.message;
  });