const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;
const HTML_FILE = path.join(__dirname, 'web', 'index.html');

app.use(express.json());
app.use(express.static(__dirname));

app.get('/', (_req, res) => res.redirect('/web/index.html'));

app.post('/update-city', (req, res) => {
  const { cityId, px, py } = req.body;
  if (!cityId || px == null || py == null) {
    return res.status(400).json({ error: 'Missing cityId, px, or py' });
  }

  let html;
  try {
    html = fs.readFileSync(HTML_FILE, 'utf8');
  } catch (err) {
    return res.status(500).json({ error: `Could not read index.html: ${err.message}` });
  }

  // Match the CITIES line for this city and replace its px/py values
  const escaped = cityId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const pattern = new RegExp(`({id:"${escaped}",[^\\n]*?)px:\\d+,\\s*py:\\d+`);
  const updated = html.replace(pattern, `$1px:${px}, py:${py}`);

  if (updated === html) {
    return res.status(404).json({ error: `City '${cityId}' not found or coordinates already match` });
  }

  try {
    fs.writeFileSync(HTML_FILE, updated, 'utf8');
  } catch (err) {
    return res.status(500).json({ error: `Could not write index.html: ${err.message}` });
  }

  console.log(`Updated ${cityId}: px=${px}, py=${py}`);
  res.json({ ok: true, cityId, px, py });
});

app.listen(PORT, () => {
  console.log(`Dev server: http://localhost:${PORT}/web/index.html?dev`);
});
