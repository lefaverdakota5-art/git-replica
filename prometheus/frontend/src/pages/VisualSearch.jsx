import React, { useEffect, useMemo, useState } from "react";
import api from "../api";

function ResultCard({ result }) {
  const category = result.category.replaceAll("_", " ");
  return (
    <article className="visual-result">
      <div className="visual-result-topline">
        <strong>{result.filename}</strong>
        <span className="visual-score">{result.score}%</span>
      </div>
      <p className="visual-category">{category}</p>
      <dl className="visual-signals">
        <div><dt>Perceptual</dt><dd>{result.signals.perceptual}%</dd></div>
        <div><dt>Histogram</dt><dd>{result.signals.color_histogram}%</dd></div>
        <div><dt>Color</dt><dd>{result.signals.average_color}%</dd></div>
        <div><dt>Dimensions</dt><dd>{result.dimensions.width} × {result.dimensions.height}</dd></div>
      </dl>
      <p className="visual-provenance">Indexed {new Date(result.indexed_at).toLocaleString()}</p>
    </article>
  );
}

export default function VisualSearch() {
  const [projects, setProjects] = useState([]);
  const [projectId, setProjectId] = useState("");
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [results, setResults] = useState([]);
  const [isWorking, setIsWorking] = useState(false);
  const fileSummary = useMemo(() => file ? `${file.name} · ${(file.size / 1024 / 1024).toFixed(2)} MB` : "Choose a JPEG, PNG, WebP, or GIF up to 25 MB.", [file]);

  useEffect(() => {
    api.listProjects().then((items) => {
      setProjects(items);
      if (items[0]) setProjectId(items[0].id);
    }).catch((error) => setStatus(`Could not load projects: ${error.message}`));
  }, []);

  const requireSelection = () => {
    if (!projectId) throw new Error("Create or select a project before using the visual library.");
    if (!file) throw new Error("Choose an image first.");
  };

  const indexImage = async () => {
    try {
      requireSelection();
      setIsWorking(true);
      const indexed = await api.indexVisualImage(projectId, file);
      setStatus(`${indexed.filename} is indexed privately in the selected project.`);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setIsWorking(false);
    }
  };

  const findMatches = async () => {
    try {
      requireSelection();
      setIsWorking(true);
      const response = await api.searchVisualImages(projectId, file);
      setResults(response.results);
      setStatus(response.result_count ? `Found ${response.result_count} local match${response.result_count === 1 ? "" : "es"}.` : "No images are indexed in this project's visual library yet.");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setIsWorking(false);
    }
  };

  return (
    <main className="visual-page">
      <header className="visual-hero">
        <p className="eyebrow">PRIVATE MULTIMODAL FOUNDATION</p>
        <h1>Visual Search</h1>
        <p>Index images you explicitly upload, then compare a query with transparent, reproducible visual evidence. This release is intentionally local-only: it does not present web-wide, face, semantic, audio, or video matching claims.</p>
      </header>

      <section className="visual-workspace" aria-label="Private visual matching workspace">
        <div className="visual-controls cyber-card">
          <label className="visual-label" htmlFor="visual-project">Project library</label>
          <select id="visual-project" className="cyber-input" value={projectId} onChange={(event) => setProjectId(event.target.value)}>
            <option value="">Select a project</option>
            {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
          </select>

          <label className="visual-dropzone" htmlFor="visual-file">
            <span className="visual-dropzone-icon">◈</span>
            <strong>Choose reference image</strong>
            <small>{fileSummary}</small>
            <input id="visual-file" type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={(event) => setFile(event.target.files?.[0] || null)} />
          </label>

          <div className="visual-actions">
            <button className="cyber-btn" onClick={indexImage} disabled={isWorking}>Index image</button>
            <button className="cyber-btn primary" onClick={findMatches} disabled={isWorking}>Find local matches</button>
          </div>
          {status && <p className="visual-status" role="status">{status}</p>}
        </div>

        <aside className="visual-method cyber-card">
          <p className="eyebrow">MATCH EVIDENCE</p>
          <h2>Multiple independent signals</h2>
          <ul>
            <li>Cryptographic SHA-256 detects exact uploaded duplicates.</li>
            <li>Difference hashing identifies resilient near-duplicate image structure.</li>
            <li>Normalized color histograms compare global palettes.</li>
            <li>Average-color distance helps explain visual similarity scores.</li>
          </ul>
          <p>Each result preserves its source filename, indexing time, dimensions, match category, and signal-level scores.</p>
        </aside>
      </section>

      <section className="visual-results" aria-live="polite">
        <div className="visual-results-heading">
          <div><p className="eyebrow">RESULTS</p><h2>Ranked local matches</h2></div>
          <span>{results.length} result{results.length === 1 ? "" : "s"}</span>
        </div>
        {results.length ? <div className="visual-grid">{results.map((result) => <ResultCard key={result.id} result={result} />)}</div> : <div className="visual-empty">Index one or more reference images, then submit an image to compare them.</div>}
      </section>
    </main>
  );
}
