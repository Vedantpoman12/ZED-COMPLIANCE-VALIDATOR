// script.js

document.addEventListener("DOMContentLoaded", function() {
    const fileInputs = [
        { input: "file1", text: "file1-name" },
        { input: "file2", text: "file2-name" },
        { input: "file3", text: "file3-name" },
    ];

    fileInputs.forEach(pair => {
        const inputEl = document.getElementById(pair.input);
        const textEl = document.getElementById(pair.text);

        inputEl.addEventListener("change", function() {
            if (inputEl.files.length > 0) {
                textEl.textContent = inputEl.files[0].name; // show filename
                textEl.style.color = "green";
            } else {
                textEl.textContent = "No file chosen";
                textEl.style.color = "#444";
            }
        });
    });
});
