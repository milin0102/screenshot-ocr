console.log("JavaScript file loaded successfully");

// Add visual feedback that JavaScript is working
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, JavaScript is working");
    
    // Add a visible indicator that JavaScript loaded
    const indicator = document.createElement('div');
    indicator.style.cssText = 'position: fixed; top: 10px; right: 10px; background: green; color: white; padding: 5px; border-radius: 3px; z-index: 1000;';
    indicator.textContent = 'JS ✓';
    document.body.appendChild(indicator);
    
    // Test if elements exist
    const elements = ['imageUpload', 'resetBtn', 'copyBtn', 'downloadBtn'];
    elements.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            console.log(`Element ${id} found`);
        } else {
            console.error(`Element ${id} NOT found`);
        }
    });
});

document.getElementById("imageUpload").addEventListener("change", handleImageUpload);
document.getElementById("resetBtn").addEventListener("click", resetOutput);
document.getElementById("copyBtn").addEventListener("click", copyText);
document.getElementById("downloadBtn").addEventListener("click", downloadText);

function showLoading() {
    document.getElementById("extractedText").value = "Processing image... Please wait.";
    document.getElementById("extractedText").classList.add("loading");
    
    const tableBody = document.querySelector("#kvTable tbody");
    tableBody.innerHTML = "<tr class='processing-row'><td colspan='2'>Processing image...</td></tr>";
    
    // Disable buttons during processing
    document.querySelectorAll("button").forEach(btn => btn.disabled = true);
}

function showError(message) {
    document.getElementById("extractedText").value = `Error: ${message}`;
    document.getElementById("extractedText").classList.remove("loading");
    document.getElementById("extractedText").classList.add("error");
    
    const tableBody = document.querySelector("#kvTable tbody");
    tableBody.innerHTML = "<tr class='error-row'><td colspan='2'>Error occurred</td></tr>";
    
    // Re-enable buttons
    document.querySelectorAll("button").forEach(btn => btn.disabled = false);
    console.error("API Error:", message);
}

function clearStates() {
    document.getElementById("extractedText").classList.remove("loading", "error");
    document.querySelectorAll("button").forEach(btn => btn.disabled = false);
}

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById("previewImg").src = e.target.result;
    };
    reader.readAsDataURL(file);

    // Show loading state
    showLoading();

    const formData = new FormData();
    formData.append("file", file);

    fetch("/api/extract", {
        method: "POST",
        body: formData
    })
    .then(response => {
        console.log("Response status:", response.status);
        console.log("Response headers:", response.headers);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Response data:", data);
        
        // Clear loading states
        clearStates();
        
        if (data.error) {
            showError(data.error);
            return;
        }

        // Update extracted text
        document.getElementById("extractedText").value = data.text || "";

        // Update key-value table
        const tableBody = document.querySelector("#kvTable tbody");
        tableBody.innerHTML = "";
        
        if (data.key_values && data.key_values.length > 0) {
            data.key_values.forEach(kv => {
                const row = document.createElement("tr");
                row.innerHTML = `<td>${kv.key || ''}</td><td>${kv.value || ''}</td>`;
                tableBody.appendChild(row);
            });
        } else {
            tableBody.innerHTML = "<tr><td colspan='2'>No key-value pairs found</td></tr>";
        }

        // Show warning if present
        if (data.warning) {
            console.warn("Warning:", data.warning);
        }
    })
    .catch(err => {
        console.error("Fetch error:", err);
        clearStates();
        showError(`Failed to process image: ${err.message}`);
    });
}

function resetOutput() {
    clearStates();
    document.getElementById("extractedText").value = "";
    document.querySelector("#kvTable tbody").innerHTML = "";
    document.getElementById("previewImg").src = "";
    document.getElementById("imageUpload").value = "";
}

function copyText() {
    const text = document.getElementById("extractedText").value;
    navigator.clipboard.writeText(text).then(() => {
        alert("Text copied!");
    });
}

function downloadText() {
    const text = document.getElementById("extractedText").value;
    const blob = new Blob([text], { type: "text/plain" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "extracted_text.txt";
    link.click();
}
