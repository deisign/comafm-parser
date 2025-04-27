const fs = require('fs');
const dayjs = require('dayjs');

function generateWeeklyChart() {
  try {
    if (!fs.existsSync('tracks.json')) {
      console.error('tracks.json not found!');
      process.exit(1);
    }

    const tracks = JSON.parse(fs.readFileSync('tracks.json', 'utf8'));

    const weekAgo = dayjs().subtract(7, 'day');
    const recentTracks = tracks.filter(track => dayjs(track.start_time).isAfter(weekAgo));

    const counter = {};

    for (const track of recentTracks) {
      const titleLower = (track.title || '').toLowerCase();
      const artistLower = (track.artist || '').toLowerCase();

      if (artistLower === 'coma.fm') {
        continue; // Пропускаем джинглы
      }

      if (titleLower.match(/monday|tuesday|wednesday|thursday|friday|saturday|sunday/)) {
        continue; // Пропускаем треки с днями недели
      }

      const key = `${track.artist} - ${track.title}`;
      counter[key] = (counter[key] || 0) + 1;
    }

    const topTracks = Object.entries(counter)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 30)
      .map(([name, count]) => ({ name, count }));

    fs.writeFileSync('weekly-charts.json', JSON.stringify(topTracks, null, 2));
    console.log(`Generated weekly-charts.json with ${topTracks.length} tracks.`);
  } catch (error) {
    console.error('Error generating weekly chart:', error);
    process.exit(1);
  }
}

generateWeeklyChart();
