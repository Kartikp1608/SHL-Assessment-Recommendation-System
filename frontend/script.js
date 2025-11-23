const submitBtn = document.getElementById("submit");
const loader = document.getElementById("loader");
const output = document.getElementById("output");

submitBtn.onclick = async () => {
    const query = document.getElementById("query").value.trim();

    if (!query) {
        alert("Enter a query.");
        return;
    }

    loader.classList.remove("hidden");
    output.innerHTML = "";

    const res = await fetch("https://cors-anywhere.herokuapp.com/http://35.223.25.198:8000/recommend", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ query })
});
    
    const data = await res.json();
    loader.classList.add("hidden");

    // Render recommended assessments
    data.recommended_assessments.forEach(item => {
        output.innerHTML += `
          <div class="card">
            <div class="card-title">${item.name}</div>

            <p><strong>URL:</strong> <a href="${item.url}" target="_blank">${item.url}</a></p>

            <p><strong>Description:</strong> ${item.description}</p>

            <p><strong>Adaptive Support:</strong> ${item.adaptive_support}</p>

            <p><strong>Remote Support:</strong> ${item.remote_support}</p>

            <p><strong>Duration:</strong> ${item.duration} minutes</p>

            <p><strong>Test Type:</strong> ${item.test_type.join(", ")}</p>
          </div>
        `;
    });
};
