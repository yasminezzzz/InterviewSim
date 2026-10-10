let sessionId = null;
let currentAudioUrl = null;
let currentQuestion = null;
let mediaRecorder = null;
let audioChunks = [];

const statusEl = document.getElementById("status");
const questionEl = document.getElementById("question");
const transcriptEl = document.getElementById("transcript");
const scoreEl = document.getElementById("score");
const reportEl = document.getElementById("report");
const historyEl = document.getElementById("history");
const player = document.getElementById("player");

document.getElementById("startBtn").onclick = startSession;
document.getElementById("speakBtn").onclick = () => playAudio(currentAudioUrl);
document.getElementById("recordBtn").onclick = startRecording;
document.getElementById("stopBtn").onclick = stopRecording;

async function startSession() {
    const profile = document.getElementById("profile").value;
    statusEl.textContent = "Démarrage…";
    reportEl.style.display = "none";
    historyEl.innerHTML = "";

    const res = await fetch("/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile, n_standard: 5, n_random: 0 }),
    });
    const data = await res.json();
    sessionId = data.session_id;

    currentQuestion = data.question;
    questionEl.textContent = data.question;
    currentAudioUrl = data.audio_url;
    transcriptEl.textContent = "(ta réponse apparaîtra ici)";
    scoreEl.textContent = "";

    playAudio(currentAudioUrl);

    document.getElementById("speakBtn").disabled = false;
    document.getElementById("recordBtn").disabled = false;
    statusEl.textContent = "À toi de répondre !";
}

function playAudio(url) {
    if (!url) return;
    player.src = url;
    player.play();
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
        mediaRecorder.onstop = sendAudio;

        mediaRecorder.start();
        statusEl.textContent = "🎤 Enregistrement...";
        document.getElementById("recordBtn").disabled = true;
        document.getElementById("stopBtn").disabled = false;
    } catch (e) {
        statusEl.textContent = "❌ Micro non autorisé";
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach((t) => t.stop());
        statusEl.textContent = "Traitement…";
        document.getElementById("stopBtn").disabled = true;
    }
}

async function sendAudio() {
    const blob = new Blob(audioChunks, { type: "audio/wav" });
    const formData = new FormData();
    formData.append("file", blob, "answer.wav");

    const res = await fetch(`/sessions/${sessionId}/audio`, {
        method: "POST",
        body: formData,
    });

    if (!res.ok) {
        statusEl.textContent = "❌ Erreur d'envoi";
        document.getElementById("recordBtn").disabled = false;
        return;
    }

    const data = await res.json();
    const transcript = data.transcript || "(vide)";
    const score = data.evaluation ? data.evaluation.score : "-";
    const quality = data.evaluation ? data.evaluation.quality : "-";

    transcriptEl.textContent = `"${transcript}"`;
    scoreEl.textContent = `📊 Score : ${score} (${quality})`;

    addTurnToHistory(currentQuestion, transcript, score, quality);

    if (data.finished) {
        showReport();
    } else {
        currentQuestion = data.next_question.question;
        questionEl.textContent = currentQuestion;
        currentAudioUrl = data.audio_url;
        playAudio(currentAudioUrl);
        statusEl.textContent = "À toi de répondre !";
        document.getElementById("recordBtn").disabled = false;
    }
}

function addTurnToHistory(question, answer, score, quality) {
    const turn = document.createElement("div");
    turn.className = "turn";
    turn.innerHTML = `
        <div class="q">❓ ${question}</div>
        <div class="a">🎤 "${answer}"</div>
        <div class="s">📊 Score : ${score} (${quality})</div>
    `;
    historyEl.appendChild(turn);
}

async function showReport() {
    const res = await fetch(`/sessions/${sessionId}/report`);
    const report = await res.json();
    reportEl.style.display = "block";
    reportEl.innerHTML = `
        <h2>Rapport final</h2>
        <p>Score global : <b>${(report.score * 100).toFixed(1)}%</b></p>
        <p>Questions : ${report.num_questions}</p>
        <p>Décision : <b>${report.decision}</b></p>
    `;
    statusEl.textContent = "Entretien terminé";
    document.getElementById("recordBtn").disabled = true;
}