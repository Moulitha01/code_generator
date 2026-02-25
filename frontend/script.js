let latestResult = null;

async function generateCode() {
    const description = document.getElementById("description").value;
    const language = document.getElementById("language").value;

    const response = await fetch("/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            description: description,
            language: language
        })
    });

    const data = await response.json();

    latestResult = data; // store for download

    document.getElementById("planning").textContent = data.planning;
    document.getElementById("design").textContent = data.design;
    document.getElementById("code").textContent = data.code;
    document.getElementById("testing").textContent = data.testing;

    // Optional summary
    document.getElementById("summary").textContent =
        "Code generated successfully using multi-agent system.";
}

function downloadReport() {
    if (!latestResult) {
        alert("Generate code first!");
        return;
    }

    const fullReport =
        "PLANNING:\n" + latestResult.planning + "\n\n" +
        "DESIGN:\n" + latestResult.design + "\n\n" +
        "CODE:\n" + latestResult.code + "\n\n" +
        "TESTING:\n" + latestResult.testing;

    const blob = new Blob([fullReport], { type: "text/plain" });

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "full_report.txt";
    document.body.appendChild(a);
    a.click();
    a.remove();
}

function downloadCode() {
    if (!latestResult) {
        alert("Generate code first!");
        return;
    }

    const blob = new Blob([latestResult.code], { type: "text/plain" });

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "generated_code.txt";
    document.body.appendChild(a);
    a.click();
    a.remove();
}

function copyCode() {
    if (!latestResult) {
        alert("Generate code first!");
        return;
    }

    navigator.clipboard.writeText(latestResult.code);
    alert("Code copied!");
}