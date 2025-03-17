
    // Liste der möglichen Videos
    const videos = ["waterball_loop.mp4", "monkey_loop.mp4", "lake_loop.mp4"];

    // Funktion zum Abrufen des gespeicherten Videos aus localStorage
    function getStoredVideo() {
        const storedData = localStorage.getItem("selectedVideo");
        if (storedData) {
            const parsedData = JSON.parse(storedData);
            const currentTime = new Date().getTime();
            
            // Prüfen, ob der gespeicherte Wert noch gültig ist (3 Minuten = 180000 Millisekunden)
            if (currentTime - parsedData.timestamp < 180000) {
                return parsedData.video; // Gespeichertes Video verwenden
            }
        }
        return null; // Kein gültiges Video gefunden
    }

    // Funktion zum Speichern des Videos in localStorage
    function storeVideo(video) {
        const data = {
            video: video,
            timestamp: new Date().getTime() // Aktueller Zeitstempel
        };
        localStorage.setItem("selectedVideo", JSON.stringify(data));
    }

    // Prüfen, ob ein gültiges Video in localStorage existiert
    let selectedVideo = getStoredVideo();

    // Falls kein gültiges Video vorhanden ist, wähle ein zufälliges aus und speichere es
    if (!selectedVideo) {
        selectedVideo = videos[Math.floor(Math.random() * videos.length)];
        storeVideo(selectedVideo);
    }

    // Video-Element mit dem gespeicherten oder neuen Video setzen
    document.getElementById("video-source").src = "/static/videos/" + selectedVideo;

    // Video neu laden, um die Quelle zu aktualisieren
    document.getElementById("background-video").load();

