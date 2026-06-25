// دالة تشفير وفك تشفير النصوص
function sendTextToPython(action) {
    const algo = document.getElementById('algo').value;
    const text = document.getElementById('textInput').value;
    const key = document.getElementById('textKey').value;

    if (!text || !key) return alert("Please fill text and key fields.");

    fetch('/api/text', {
        method: 'POST',
        body: JSON.stringify({ algo, action, text, key })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('textResultContainer').style.display = 'block';
        document.getElementById('textResultValue').innerText = data.result;
    });
}

// دالة معالجة الميديا والملفات الكبيرة عبر المتصفح مباشرة وبسرعة فائقة
function uploadAndProcessMedia() {
    const fileInput = document.getElementById('fileChooser');
    const key = document.getElementById('mediaKey').value;
    
    if (fileInput.files.length === 0) return;
    if (!key) return alert("Please enter a key.");

    const file = fileInput.files[0];
    
    document.getElementById('mediaResultContainer').style.display = 'block';
    document.getElementById('mediaResultValue').innerText = "Processing file via browser native speed... Downloading shortly!";

    // قراءة الملف كبايتات ثنائية نقية داخل المتصفح لإرسالها بأعلى سرعة
    const reader = new FileReader();
    reader.onload = function(e) {
        const arrayBuffer = e.target.result;

        // إرسال البايتات الصافية للبايثون مع تمرير المفتاح واسم الملف في الـ Headers
        fetch('/api/media', {
            method: 'POST',
            headers: {
                'X-Crypto-Key': key,
                'X-File-Name': encodeURIComponent(file.name)
            },
            body: arrayBuffer
        })
        .then(response => response.blob())
        .then(blob => {
            // تحميل الملف المعالج فوراً إلى مجلد الـ Downloads بجهازك
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            let outputName = file.name.startsWith("Encrypted_") ? file.name.replace("Encrypted_", "Decrypted_") : "Encrypted_" + file.name;
            a.download = outputName;
            document.body.appendChild(a);
            a.click();
            a.remove();
            
            document.getElementById('mediaResultValue').innerText = "Success! File processed and downloaded into your Downloads folder.";
            fileInput.value = ""; 
        })
        .catch(err => {
            document.getElementById('mediaResultValue').innerText = "Error: " + err;
        });
    };
    
    reader.readAsArrayBuffer(file);
}

function copyToClipboard() {
    const textToCopy = document.getElementById('textResultValue').innerText;
    if (!textToCopy) return;

    navigator.clipboard.writeText(textToCopy).then(() => {
        const copyBtn = document.getElementById('copyBtn');
        copyBtn.innerText = "Copied! ✓";
        copyBtn.style.background = "#10b981";
        setTimeout(() => {
            copyBtn.innerText = "Copy 📋";
            copyBtn.style.background = "#4f46e5";
        }, 2000);
    });
}