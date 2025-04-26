const axios = require("axios");
const fs = require("fs");

async function fetchTracks() {
  const stationId = "s4360dbc20";
  const url = `https://public.radio.co/stations/${stationId}/history`;

  let existingTracks = [];
  const tracksFile = "tracks.json";

  if (fs.existsSync(tracksFile)) {
    const rawData = fs.readFileSync(tracksFile, "utf-8");
    existingTracks = JSON.parse(rawData);
  }

  try {
    console.log("Fetching history from Radio.co...");
    const { data } = await axios.get(url, {
      headers: {
        "User-Agent": "Mozilla/5.0"
      }
    });

    const history = data.tracks || [];
    console.log(`Fetched ${history.length} tracks from history.`);

    let newTracks = 0;

    history.forEach(item => {
      if (item.title && item.start_time) {
        const exists = existingTracks.some(t => t.time === item.start_time);
        if (!exists) {
          let artist = null;
          let trackTitle = item.title.trim();
          if (trackTitle.includes(" - ")) {
            const parts = trackTitle.split(" - ");
            artist = parts[0].trim();
            trackTitle = parts.slice(1).join(" - ").trim();
          }
          existingTracks.push({
            artist: artist,
            title: trackTitle,
            time: item.start_time,
            artwork_url: item.artwork_url || null
          });
          newTracks++;
        }
      }
    });

    console.log(`Added ${newTracks} new tracks.`);

    existingTracks.sort((a, b) => new Date(b.time) - new Date(a.time));

    fs.writeFileSync(tracksFile, JSON.stringify(existingTracks, null, 2), "utf-8");
    console.log("Updated tracks.json successfully.");
  } catch (error) {
    console.error("Error fetching history:", error.message);
  }
}

fetchTracks();
