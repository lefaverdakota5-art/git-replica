const BASE = "";

async function req(method, path, body) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(BASE + path, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

const api = {
  // Health
  health: () => req("GET", "/api/health"),
  stats: () => req("GET", "/api/stats"),

  // Projects
  listProjects: () => req("GET", "/api/projects"),
  createProject: (data) => req("POST", "/api/projects", data),
  getProject: (id) => req("GET", `/api/projects/${id}`),
  updateProject: (id, data) => req("PUT", `/api/projects/${id}`, data),
  deleteProject: (id) => req("DELETE", `/api/projects/${id}`),

  // Files
  listFiles: (projectId) => req("GET", `/api/projects/${projectId}/files`),
  readFile: (projectId, path) => req("GET", `/api/projects/${projectId}/files/${path}`),
  createFile: (projectId, path, content) =>
    req("POST", `/api/projects/${projectId}/files/${path}`, { content }),
  updateFile: (projectId, path, content) =>
    req("PUT", `/api/projects/${projectId}/files/${path}`, { content }),
  deleteFile: (projectId, path) =>
    req("DELETE", `/api/projects/${projectId}/files/${path}`),

  // Code generation
  generate: (prompt, language, project_id) =>
    req("POST", "/api/generate", { prompt, language, project_id }),
  complete: (code, language, line) =>
    req("POST", "/api/complete", { code, language, line }),
  scaffold: (data) => req("POST", "/api/scaffold", data),
  generateDocstring: (code, language) =>
    req("POST", "/api/generate/docstring", { code, language }),
  generateTypes: (code, language) =>
    req("POST", "/api/generate/types", { code, language }),
  generateImports: (code, language) =>
    req("POST", "/api/generate/imports", { code, language }),

  // Templates
  listTemplates: () => req("GET", "/api/templates"),

  // Execution
  runProject: (projectId) => req("POST", `/api/projects/${projectId}/run`),
  execCommand: (projectId, command, timeout = 30) =>
    req("POST", `/api/projects/${projectId}/exec`, { command, timeout }),

  // Git
  gitInit: (projectId) => req("POST", `/api/projects/${projectId}/git/init`),
  gitCommit: (projectId, message, files = []) =>
    req("POST", `/api/projects/${projectId}/git/commit`, { message, files }),
  gitLog: (projectId) => req("GET", `/api/projects/${projectId}/git/log`),
  gitDiff: (projectId, ref = "HEAD") =>
    req("POST", `/api/projects/${projectId}/git/diff`, { ref }),

  // Packages
  installPackages: (projectId, packages, manager = "pip") =>
    req("POST", `/api/projects/${projectId}/packages/install`, { packages, manager }),

  // Deploy
  createDeploy: (projectId, config = {}) =>
    req("POST", `/api/projects/${projectId}/deploy`, { port: 8000, env_vars: {}, ...config }),
  getDeploy: (projectId) => req("GET", `/api/projects/${projectId}/deploy`),
};

export default api;
