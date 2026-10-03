const form = document.getElementById("comicForm");
const button = document.getElementById("generateBtn");
const statusBox = document.getElementById("status");
const result = document.getElementById("result");

let currentComic = null;


// ===============================
// GENERATE COMIC
// ===============================

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    button.disabled = true;
    button.textContent = "Generating...";
    statusBox.textContent = "Creating your comic story...";
    result.classList.add("hidden");

    const payload = {
        prompt: document.getElementById("prompt").value,
        style: document.getElementById("style").value,
        language: document.getElementById("language").value,
        panels: Number(document.getElementById("panels").value)
    };

    try {
        const response = await fetch("/api/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Comic generation failed."
            );
        }

        renderComic(data);

        statusBox.textContent =
            "Comic generated successfully!";

    } catch (error) {

        console.error(error);

        statusBox.textContent =
            error.message;

    } finally {

        button.disabled = false;
        button.textContent = "Generate Comic";
    }
});


// ===============================
// ESCAPE HTML
// ===============================

function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// ===============================
// RENDER COMIC
// ===============================

function renderComic(comic) {

    // VERY IMPORTANT:
    // Save the generated comic globally
    // so the PDF button can use it.

    currentComic = comic;

    console.log(
        "Comic saved for PDF:",
        currentComic
    );

    const panels = comic.panels.map(panel => {

        const dialogue = (panel.dialogue || [])
            .map(line => `
                <div class="dialogue">
                    ${escapeHtml(line)}
                </div>
            `)
            .join("");

        return `
            <article class="panel">

                <h3>
                    Panel ${escapeHtml(panel.panel)}:
                    ${escapeHtml(panel.title)}
                </h3>

                <p>
                    <b>Scene:</b>
                    ${escapeHtml(panel.scene_description)}
                </p>

                <p>
                    <b>Narration:</b>
                    ${escapeHtml(panel.narration)}
                </p>

                ${dialogue}

            </article>
        `;

    }).join("");


    result.innerHTML = `

        <div class="card">

            <h2>
                ${escapeHtml(comic.title)}
            </h2>

            <p class="meta">
                Style:
                ${escapeHtml(comic.style)}
                ·
                Language:
                ${escapeHtml(comic.language)}
            </p>

            <p>
                <b>Characters:</b>
                ${comic.characters
                    .map(character => escapeHtml(character))
                    .join(", ")}
            </p>

            ${panels}

            <button id="pdfBtn">
                Download Comic as PDF
            </button>

            <div id="pdfStatus" class="status"></div>

        </div>
    `;

    result.classList.remove("hidden");

    document
        .getElementById("pdfBtn")
        .addEventListener("click", downloadPDF);
}


// ===============================
// DOWNLOAD PDF
// ===============================

async function downloadPDF() {

    const pdfBtn =
        document.getElementById("pdfBtn");

    const pdfStatus =
        document.getElementById("pdfStatus");


    if (!currentComic) {

        pdfStatus.textContent =
            "No comic is available for PDF export.";

        return;
    }


    pdfBtn.disabled = true;

    pdfStatus.textContent =
        "Preparing PDF...";


    try {

        console.log(
            "Sending comic to PDF exporter:",
            currentComic
        );


        const response = await fetch(
            "/api/export",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(currentComic)
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "PDF export failed."
            );
        }


        console.log(
            "PDF response:",
            data
        );


        if (!data.download_url) {

            throw new Error(
                "PDF was created, but no download URL was returned."
            );
        }


        pdfStatus.textContent =
            "PDF ready. Downloading...";


        // Start browser download
        window.location.href =
            data.download_url;


    } catch (error) {

        console.error(
            "PDF ERROR:",
            error
        );

        pdfStatus.textContent =
            error.message;

        pdfBtn.disabled = false;
    }
}