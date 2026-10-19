from flask import Flask, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # Permite que tu frontend en Netlify se conecte sin problemas de CORS

# Canales/transmisiones oficiales de hipódromos
STREAMS_CONFIG = {
    "gulfstream": "https://www.youtube.com/@GulfstreamParkRacetrack/live",
    "rinconada": "https://www.youtube.com/@INHOFICIAL/live",
    "monterrico": "https://www.youtube.com/@HipodromoDeMonterricoOficial/live",
    "tvg": "https://www.youtube.com/@FanDuelTV/live"
}

def get_live_m3u8(url):
    """ Extrae el enlace HLS (.m3u8) directo y activo de la transmisión """
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('url', None)
    except Exception as e:
        print(f"Error extrayendo stream: {e}")
        return None

@app.route('/api/stream/<hipodromo>', methods=['GET'])
def stream_handler(hipodromo):
    target_url = STREAMS_CONFIG.get(hipodromo.lower())
    if not target_url:
        return jsonify({"status": "error", "message": "Hipódromo no configurado"}), 404
    
    m3u8_link = get_live_m3u8(target_url)
    
    if m3u8_link:
        return jsonify({
            "status": "success",
            "hipodromo": hipodromo,
            "m3u8_url": m3u8_link
        })
    else:
        # Respaldo si el hipódromo no está transmitiendo en vivo en este instante
        return jsonify({
            "status": "offline",
            "message": "En este momento el hipódromo no tiene carrera en vivo activa",
            "fallback_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)