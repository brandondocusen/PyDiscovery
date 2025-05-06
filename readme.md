# PyDiscovery

> *Transform Python codebases into token-efficient knowledge graphs for LLMs*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Dependencies: None](https://img.shields.io/badge/dependencies-none-green.svg)](#features-at-a-glance)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)



## 📖 Overview

PyDiscovery elegantly maps Python projects into compact, LLM-optimized knowledge graphs with a single command. It captures the essence of your codebase—structure, relationships, dependencies—all without external libraries.

```bash
python launcher.py /path/to/your/project
```

The result: a token-efficient `knowledge_graph.json` file, perfect for enhancing LLM understanding of your code.

## ✨ Features at a Glance

| Domain | What PyDiscovery Captures and Provides |
|:-------|:--------------------------|
| **Static Analysis** | Classes, functions, attributes, inheritance, imports, data flows |
| **Environment** | Third-party packages with installed versions |
| **Runtime Analysis** | Optional caller → callee relationships with timing metrics |
| **API** | Optional lightweight HTTP endpoint serving the knowledge graph |

## 🚀 Getting Started

### Static Analysis (Core Feature)

```bash
# Clone the repository
git clone https://github.com/your-org/pydiscovery.git
cd pydiscovery

# Run analysis on any Python project
python launcher.py /path/to/your/project
```

<details>
<summary>📄 Example Output Structure</summary>

```json
{
  "root": "C:/projects/my_app",
  "files": ["app/core.py", "app/views.py"],
  "elements": [
    {
      "id": "13f0…",
      "type": "CLASS",
      "name": "UserService",
      "dependencies": ["AuthRepo", "typing.List"],
      "metadata": {"ctor_params": ["repo"]}
    }
  ],
  "data_flows": {"app/core.py": {"variables": {...}}},
  "external_dependencies": [
    {"package": "requests", "version": "2.31.0", "used_by": ["app/http.py"]}
  ],
  "analysis_id": "uuid-v4"
}
```

</details>

### Runtime Tracing (Advanced)

Capture actual execution patterns with the `pdtrace.py` utility:

```bash
python pdtrace.py <target> [--chdir] [--] [args …]
```

Where `<target>` can be:
- A single `.py` file
- A folder containing Python files
- An importable package name

<details>
<summary>📊 Runtime Tracing Examples</summary>

| Scenario | Command |
|:---------|:--------|
| **Single script** | `python pdtrace.py C:\proj\build.py` |
| **Tool directory** | `python pdtrace.py C:\tools --chdir` |
| **Installed package** | `python pdtrace.py my_package -- arg1 arg2` |

The output includes:
- A `runtime_calls.json` file in the PyDiscovery directory alongside the static knowledge graph
- A summary of calls captured and timing information

```
[pdtrace] saved 412 calls to …\runtime_calls.json in 2.3 s
[pdtrace] ✅ success – runtime call-graph captured.
[pdtrace] 📄 Trace file ready at pydiscovery\runtime_calls.json
```

</details>

### HTTP API (Optional)

Serve your knowledge graph for automatic coding integrations or dashboards:

```python
from pathlib import Path
from pydiscovery.repository.in_memory_repository import InMemoryCodeElementRepository
from pydiscovery.analyzer.code_analyzer import CodeAnalyzer
from pydiscovery.api_server import serve

repo = InMemoryCodeElementRepository()
CodeAnalyzer(repo).analyse_path(Path("/path/to/your/project"))
serve(repo, port=9000)  # Access at http://localhost:9000/elements
```

## 🔄 Workflow Integration

PyDiscovery fits seamlessly into your development process:

1. **Analyze** after significant code changes
2. **Prompt** LLMs with the knowledge graph for explanations or refactoring suggestions
3. **Trace** runtime behavior when performance or coverage matters
4. **Expose** the graph via API for dashboards or CI/CD integration

## ❓ Frequently Asked Questions

| Question | Answer |
|:---------|:-------|
| How large is the output JSON? | A few kilobytes for small projects with no duplicated edges |
| Does it merge outputs? | No—each run creates a fresh file for simplicity |
| How are non-Python files handled? | Gracefully ignored during analysis |
| Can I extend the analysis? | Yes—add a class in `pydiscovery/analyzer/` that inherits from `Analyzer` |
| What Python versions are supported? | Python 10+ (standard library only) |

## 🤝 Contributing

We maintain a strict zero-dependency philosophy:

1. Fork and create a feature branch
2. Add concise tests for new analyzers
3. Submit a pull request

## 📜 License

PyDiscovery is available under the [MIT License](LICENSE), making it freely available for both personal and commercial use.

---

<div align="center">
  <i>Unlock the structure of your Python codebase</i>
</div>
