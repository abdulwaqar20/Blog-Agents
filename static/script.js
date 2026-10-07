const $ = id => document.getElementById(id);
const MAX_RETRIES = 2;

function setNode(name, state) {
  $("node-" + name).className = "node " + state;
}

function setStatus(text, cls) {
  const s = $("status");
  s.textContent = text;
  s.className = "pill " + cls;
}

function log(text, cls = "") {
  const d = document.createElement("div");
  d.className = "log-item " + cls;
  d.textContent = text;
  $("log").appendChild(d);
}

function reset() {
  ["planner", "worker", "reviewer"].forEach(n => setNode(n, ""));
  $("log").innerHTML = "";
  $("draft").innerHTML = "";
  $("outline").innerHTML = "";
  $("feedback").textContent = "Waiting for reviewer...";
  $("feedback").className = "body muted";
  $("retries").textContent = "0 / " + MAX_RETRIES;
  $("words").textContent = "0";
}

function run() {
  const topic = $("topic").value.trim();
  if (!topic) return;
  reset();
  $("runBtn").disabled = true;
  setStatus("Running", "running");
  setNode("planner", "active");

  let finished = false;
  const es = new EventSource("/run?topic=" + encodeURIComponent(topic));

  es.onmessage = e => {
    const m = JSON.parse(e.data);

    if (m.node === "__end__") {
      finished = true;
      es.close();
      $("runBtn").disabled = false;
      return;
    }

    const d = m.data;

    if (m.node === "planner") {
      setNode("planner", "done");
      setNode("worker", "active");
      $("outline").innerHTML = marked.parse(d.outline || "");
      log("Planner wrote the outline", "ok");
    }

    if (m.node === "worker") {
      setNode("worker", "done");
      setNode("reviewer", "active");
      $("draft").innerHTML = marked.parse(d.draft || "");
      $("words").textContent = (d.draft || "").split(/\s+/).filter(Boolean).length;
      log("Worker wrote a draft", "ok");
    }

    if (m.node === "reviewer") {
      $("feedback").textContent = d.feedback || "";
      $("feedback").className = "body";
      $("retries").textContent = d.retries + " / " + MAX_RETRIES;

      if (d.approved) {
        setNode("reviewer", "done");
        setStatus("Approved", "approved");
        log("Reviewer approved", "ok");
      } else {
        setNode("reviewer", "rejected");
        if (d.retries >= MAX_RETRIES) {
          setStatus("Rejected: limit reached", "warn");
          log("Reviewer rejected. Retry limit reached, returning last draft", "bad");
        } else {
          setStatus("Rejected: retrying", "rejected");
          log("Reviewer rejected. Sending back to worker", "bad");
          setNode("worker", "active");
        }
      }
    }
  };

  es.onerror = () => {
    es.close();
    $("runBtn").disabled = false;
    if (!finished) {
      setStatus("Error", "rejected");
      log("Connection or server error. Check the terminal.", "bad");
    }
  };
}

document.querySelectorAll(".tab").forEach(btn => {
  btn.onclick = () => {
    document.querySelectorAll(".tab").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".pane").forEach(p => p.classList.add("hidden"));
    btn.classList.add("active");
    $(btn.dataset.tab).classList.remove("hidden");
  };
});

$("topic").addEventListener("keydown", e => { if (e.key === "Enter") run(); });