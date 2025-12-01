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

    html = f"""
<html>
    <head>
        <title>Personas</title>
            <meta name="viewport" content="width=device-width,initial-scale=1" />
            <style>
              body {{ font-family: Arial, sans-serif; padding:20px; }}
              video {{ max-width:100%; border:1px solid #ddd; }}
              #scanner-ui {{ margin-top:20px; }}
              #result {{ margin-top:10px; font-weight:600; color:green; }}
            </style>
        </head>
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


<hr>

<h2>Escanear PDF417 (cámara)</h2>

<style>
#scanner-ui {
    margin-top: 10px;
    position: relative;
    width: fit-content;
}

#video {
    width: 350px;
    max-width: 100%;
    border-radius: 12px;
    filter: brightness(1.2);
}

.scan-box {
    position: absolute;
    top: 10%;
    left: 50%;
    transform: translateX(-50%);
    width: 70%;
    height: 60%;
    border: 3px solid #00ff99;
    border-radius: 10px;
    box-shadow: 0 0 10px #00ff99;
    pointer-events: none;
}

.laser {
    position: absolute;
    left: 0;
    width: 100%;
    height: 3px;
    background: rgba(255, 0, 0, 0.85);
    animation: laserMove 1.4s infinite alternate ease-in-out;
}

@keyframes laserMove {
    from { top: 10%; }
    to   { top: 68%; }
}

.blur-bg {
    filter: blur(5px);
}
</style>



<audio id="beep" src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg"></audio>

<script src="https://unpkg.com/@zxing/library@0.18.6/umd/index.min.js"></script>

<script>
(function () {
    let stream = null;
    let scanInterval = null;
    let barcodeDetector = null;

    const video = document.getElementById("video");
    const startBtn = document.getElementById("startBtn");
    const stopBtn = document.getElementById("stopBtn");
    const statusEl = document.getElementById("status");
    const resultEl = document.getElementById("resultText");
    const beep = document.getElementById("beep");

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
            document.body.classList.add("blur-bg");
            statusEl.textContent = "Escaneando...";

            if ("BarcodeDetector" in window) {
                try {
                    const supported = await BarcodeDetector.getSupportedFormats();
                    if (supported.includes("pdf417")) {
                        barcodeDetector = new BarcodeDetector({ formats: ["pdf417"] });
                    }
                } catch (e) {}
            }

            if (barcodeDetector) {
                scanInterval = setInterval(detectWithBarcodeDetector, 250);
            } else {
                scanInterval = setInterval(detectWithZXing, 300);
            }

        } catch (err) {
            alert("No se pudo acceder a la cámara: " + err.message);
        }
    }

    async function detectWithBarcodeDetector() {
        try {
            const codes = await barcodeDetector.detect(video);
            if (codes.length > 0) onDetected(codes[0].rawValue);
        } catch (_) {}
    }

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
            if (result) onDetected(result.text);
        } catch (_) {}
    }

    function onDetected(raw) {
        console.log("✔ Detectado:", raw);
        resultEl.textContent = raw;
        beep.play();
        stopCamera();

        const partes = raw.split('@');
        if (partes.length < 7) return;

        //document.getElementById("nombre").value = partes[2];
        //document.getElementById("apellido").value = partes[1];
        //document.getElementById("dni").value = partes[4];


        const yyyy = partes[6].substring(0, 4);
        const mm = partes[6].substring(4, 6);
        const dd = partes[6].substring(6, 8);

        //document.getElementById("fecha_nacimiento").value = `${yyyy}-${mm}-${dd}`;
    }

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
        statusEl.textContent = "Cámara apagada.";
        document.body.classList.remove("blur-bg");
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
