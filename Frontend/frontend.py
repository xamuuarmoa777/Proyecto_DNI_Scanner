

# frontend.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx

app = FastAPI()

BACKEND_URL = "http://localhost:8000"  # tu backend

@app.get("/", response_class=HTMLResponse)
async def index():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BACKEND_URL}/personas/")
        personas = r.json()

    html = """
        
<html>
<head>
<head><title>Personas</title></head>
        <body>
            <h1>Listado de Personas</h1>
            <ul>
    """
    for p in personas:
        html += f"<li>{p['id']} - {p['nombre']} {p['apellido']} (DNI: {p['dni']})</li>"

    html += """
            </ul>
            <h2>Agregar Persona</h2>
           <form action="/add" method="post">
    Nombre: <input type="text" name="nombre" id="nombre"><br>
    Apellido: <input type="text" name="apellido" id="apellido"><br>
    DNI: <input type="text" name="dni" id="dni"><br>
    Dirección: <input type="text" name="direccion" id="direccion"><br>
    Género: <input type="text" name="genero" id="genero"><br>
    Fecha Nac: <input type="date" name="fecha_nacimiento" id="fecha_nacimiento"><br>

    <input type="submit" value="Crear">
</form>

            <hr>


            <h2>Escanear PDF417 (cámara)</h2>
            <div id="scanner-ui">
                <video id="video" playsinline></video><br>
                <button id="startBtn">Iniciar escáner PDF417</button>
                <button id="stopBtn" disabled>Detener</button>
                <div id="result">Resultado: <span id="resultText">—</span></div>
            </div>
             <!-- ZXing fallback -->
<script src="https://unpkg.com/@zxing/library@0.18.6/umd/index.min.js"></script>

<script>
(function () {

    let stream = null;
    let scanInterval = null;
    let barcodeDetector = null;

    const video = document.getElementById("video");
    const startBtn = document.getElementById("startBtn");
    const stopBtn = document.getElementById("stopBtn");
    const resultEl = document.getElementById("resultText");

    // ------------------------------
    //  INICIAR CÁMARA
    // ------------------------------
    async function startCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: "environment" },
                audio: false
            });

            video.srcObject = stream;
            await video.play();

            startBtn.disabled = true;
            stopBtn.disabled = false;

            // ----- BarcodeDetector nativo -----
            if ("BarcodeDetector" in window) {
                try {
                    const supported = await BarcodeDetector.getSupportedFormats();

                    if (supported.includes("pdf417")) {
                        barcodeDetector = new BarcodeDetector({ formats: ["pdf417"] });
                        console.log("✔ BarcodeDetector PDF417 soportado");
                    } else {
                        console.warn("BarcodeDetector NO soporta PDF417 en este navegador.");
                    }
                } catch (e) {
                    console.warn("Error consultando BarcodeDetector:", e);
                }
            }

            // ----- Método de escaneo -----
            if (barcodeDetector) {
                scanInterval = setInterval(detectWithBarcodeDetector, 250);
            } else {
                console.warn("Usando ZXing como fallback");
                scanInterval = setInterval(detectWithZXing, 300);
            }

        } catch (err) {
            console.error("Error cámara:", err);
            alert("No se pudo acceder a la cámara: " + err.message);
        }
    }

    // ------------------------------
    //  DETECCIÓN CON BarcodeDetector
    // ------------------------------
    async function detectWithBarcodeDetector() {
        try {
            const codes = await barcodeDetector.detect(video);
            if (codes.length > 0) {
                const raw = codes[0].rawValue;
                onDetected(raw);
            }
        } catch (e) {
            console.warn("Error detect BarcodeDetector:", e);
        }
    }

    // ------------------------------
    //  DETECCIÓN CON ZXing fallback
    // ------------------------------
    function captureFrame() {
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0);
        return canvas;
    }

    async function detectWithZXing() {
        try {
            const canvas = captureFrame();
            const dataUrl = canvas.toDataURL("image/png");

            if (!window._reader) {
                window._reader = new ZXing.BrowserPDF417Reader();
            }

            const result = await window._reader.decodeFromImage(undefined, dataUrl);
            if (result) {
                onDetected(result.text);
            }

        } catch (_) {
            // normal cuando no detecta nada
        }
    }
   function parseDNI(raw) {
    const p = raw.split("@");
    if (p.length < 7) {
        console.warn("Formato desconocido del DNI:", raw);
        return null;
    }

    const apellido = p[1];
    const nombre = p[2];
    const dni = p[4];
    const fechaNac = p[6];  // Puede venir como DD/MM/YYYY o YYYYMMDD

    let yyyy, mm, dd;

    // Caso 1: DD/MM/YYYY
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(fechaNac)) {
        [dd, mm, yyyy] = fechaNac.split("/");
    }
    // Caso 2: YYYYMMDD
    else if (/^\d{8}$/.test(fechaNac)) {
        yyyy = fechaNac.substring(0, 4);
        mm   = fechaNac.substring(4, 6);
        dd   = fechaNac.substring(6, 8);
    }
    else {
        console.warn("Formato de fecha desconocido:", fechaNac);
        return null;
    }

    return {
        nombre,
        apellido,
        dni,
        fecha_nacimiento: `${yyyy}-${mm}-${dd}`,
    };
}



    // ------------------------------
    //  CUANDO SE LEE UN CÓDIGO
    // ------------------------------
    async function onDetected(decodedText) {
    
    if (!decodedText) return;

    resultEl.textContent = decodedText;
    stopCamera();


    const datos = parseDNI(decodedText);
    if (!datos) return;

document.getElementsByName("nombre")[0].value = datos.nombre;
document.getElementsByName("apellido")[0].value = datos.apellido;
document.getElementsByName("dni")[0].value = datos.dni;
document.getElementsByName("fecha_nacimiento")[0].value = datos.fecha_nacimiento;


    // OPCIONAL: enviar al backend
    try {
        await fetch("http://localhost:8000/personas/scan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ raw: decodedText })
        });
    } catch (err) {
        console.warn("Error enviando al backend:", err);
    }
}

    // ------------------------------
    //  DETENER CÁMARA
    // ------------------------------
    function stopCamera() {
        if (scanInterval) {
            clearInterval(scanInterval);
            scanInterval = null;
        }

        if (stream) {
            stream.getTracks().forEach(t => t.stop());
            stream = null;
        }

        video.pause();
        video.srcObject = null;

        startBtn.disabled = false;
        stopBtn.disabled = true;
    }

    startBtn.addEventListener("click", startCamera);
    stopBtn.addEventListener("click", stopCamera);

})();
</script>


        </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/add")
async def add_persona(
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    direccion: str = Form(""),
    genero: str = Form(""),
    fecha_nacimiento: str = Form("")
):
    data = {
        "nombre": nombre,
        "apellido": apellido,
        "dni": dni,
        "direccion": direccion or None,
        "genero": genero or None,
        "fecha_nacimiento": fecha_nacimiento or None,
    }
    async with httpx.AsyncClient() as client:
        await client.post(f"{BACKEND_URL}/personas/", json=data)

    return RedirectResponse("/", status_code=303)


