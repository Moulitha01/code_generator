async function generateCode() {
  const description = document.getElementById("description").value;
  const language = document.getElementById("language").value;

  const response = await fetch("/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description, language })
  });

  const data = await response.json();

  document.getElementById("planning").innerText = data.planning;
  document.getElementById("design").innerText = data.design;
  document.getElementById("code").innerText = data.code;
  document.getElementById("testing").innerText = data.testing;
}
