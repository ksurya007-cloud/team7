const task = document.getElementById("task");
const level = document.getElementById("level");
const levelLabel = document.getElementById("levelLabel");
const inputText = document.getElementById("inputText");
const inputLabel = document.getElementById("inputLabel");
const runBtn = document.getElementById("runBtn");
const result = document.getElementById("result");
const copyBtn = document.getElementById("copyBtn");
const status = document.getElementById("status");

const labels = {
  qa: ["Your question", "Example: Which is the largest ocean?"],
  explain: ["Topic to explain", "Example: Explain the Pythagoras theorem"],
  quiz: ["Topic or passage", "Paste a lesson or enter a topic"],
  summarize: ["Text to summarize", "Paste the passage you want to summarize"],
  learn: ["Topic", "Example: SQL"]
};

function updateForm() {
  const [label, placeholder] = labels[task.value];
  inputLabel.textContent = label;
  inputText.placeholder = placeholder;
  const isLearn = task.value === "learn";
  level.classList.toggle("hidden", !isLearn);
  levelLabel.classList.toggle("hidden", !isLearn);
}

task.addEventListener("change", updateForm);
updateForm();

async function checkHealth() {
  try {
    const r = await fetch("/health");
    const data = await r.json();
    status.textContent = data.ai_configured ? `AI ready • ${data.model}` : "API key required";
  } catch {
    status.textContent = "Backend offline";
  }
}
checkHealth();

function showText(text) {
  result.classList.remove("empty");
  result.textContent = text;
}

function showQuiz(data) {
  result.classList.remove("empty");
  if (data.error) {
    result.textContent = data.error;
    return;
  }
  result.innerHTML = "";
  data.questions.forEach((q, i) => {
    const box = document.createElement("div");
    box.className = "quiz-question";
    const title = document.createElement("h3");
    title.textContent = `${i + 1}. ${q.question}`;
    box.appendChild(title);

    q.options.forEach((option, idx) => {
      const letter = String.fromCharCode(65 + idx);
      const btn = document.createElement("button");
      btn.className = "option";
      btn.textContent = `${letter}. ${option}`;
      btn.onclick = () => {
        const buttons = box.querySelectorAll(".option");
        buttons.forEach(b => b.disabled = true);
        if (letter === q.answer) btn.classList.add("correct");
        else {
          btn.classList.add("wrong");
          buttons.forEach((b, j) => {
            if (String.fromCharCode(65 + j) === q.answer) b.classList.add("correct");
          });
        }
        const explanation = document.createElement("p");
        explanation.textContent = q.explanation || `Correct answer: ${q.answer}`;
        box.appendChild(explanation);
      };
      box.appendChild(btn);
    });
    result.appendChild(box);
  });
}

runBtn.onclick = async () => {
  const text = inputText.value.trim();
  if (!text) {
    showText("Please enter something first.");
    return;
  }

  const endpoint = {
    qa: "/qa",
    explain: "/explain",
    quiz: "/quiz",
    summarize: "/summarize",
    learn: "/learn/recommendations"
  }[task.value];

  const body = task.value === "qa"
    ? { question: text }
    : task.value === "learn"
      ? { topic: text, level: level.value }
      : { text };

  runBtn.disabled = true;
  runBtn.textContent = "Thinking…";
  showText("Generating your result…");

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = await response.json();

    if (!response.ok) throw new Error(data.detail || "Request failed");

    if (task.value === "quiz") showQuiz(data.result);
    else showText(data.result);
  } catch (error) {
    showText(`Error: ${error.message}`);
  } finally {
    runBtn.disabled = false;
    runBtn.textContent = "Generate Answer";
  }
};

copyBtn.onclick = async () => {
  const text = result.innerText.trim();
  if (!text || result.classList.contains("empty")) return;
  await navigator.clipboard.writeText(text);
  copyBtn.textContent = "Copied!";
  setTimeout(() => copyBtn.textContent = "Copy", 1200);
};
