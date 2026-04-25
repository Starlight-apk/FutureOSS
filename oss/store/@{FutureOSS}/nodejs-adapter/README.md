# @FutureOSS/nodejs-adapter

**Pure Node.js Runtime Adapter Service**

## Overview

This plugin is a **service provider only**. It does not contain its own business logic or `pkg` directory with code to run. Instead, it exposes a standardized API for **other plugins** to execute Node.js and npm commands within *their own* `./pkg` directories.

## Architecture

```
┌─────────────────┐      ┌──────────────────────┐      ┌─────────────────┐
│  Consumer       │      │  nodejs-adapter      │      │  Consumer's     │
│  Plugin         │─────▶│  (Service Provider)  │─────▶│  ./pkg          │
│  (e.g., web-app)│      │                      │      │  (Node.js proj) │
└─────────────────┘      └──────────────────────┘      └─────────────────┘
```

## Features

- **Context Switching**: Automatically switches working directory to the calling plugin's `./pkg` folder
- **Dependency Isolation**: Ensures npm installs packages into the caller's isolated directory
- **Full npm Support**: Install packages, run scripts, execute files
- **Stateless**: No internal state, pure service provider

## Usage for Plugin Developers

### 1. Declare Dependency

In your plugin's `manifest.json`:

```json
{
  "name": "@MyOrg/my-web-plugin",
  "dependencies": {
    "adapters": ["@FutureOSS/nodejs-adapter"]
  }
}
```

### 2. Create Your pkg Directory

```bash
my-web-plugin/
├── manifest.json
├── main.py
└── pkg/              # ← Your Node.js project lives here
    ├── package.json
    ├── index.js
    └── node_modules/ # ← Dependencies installed here
```

### 3. Use the Adapter in Your Code

```python
def init(context):
    # Get the adapter service
    adapter = context['services']['nodejs-adapter']
    
    # Install dependencies (runs 'npm install' in ./pkg)
    result = adapter.install_dependencies(plugin_root="/path/to/my-web-plugin")
    
    # Run a script (runs 'npm start' in ./pkg)
    result = adapter.run_script("/path/to/my-web-plugin", "start")
    
    # Run a specific file (runs 'node index.js' in ./pkg)
    result = adapter.run_file("/path/to/my-web-plugin", "index.js")
    
    return {'status': 'active'}
```

## API Reference

### `execute_in_context(plugin_root, command_args, is_npm=False)`

Low-level method to execute any command.

### `install_dependencies(plugin_root, packages=None)`

Install npm packages. If `packages` is None, runs `npm install` (reads from package.json).

### `run_script(plugin_root, script_name, extra_args=None)`

Run an npm script (e.g., `start`, `build`, `test`).

### `run_file(plugin_root, file_path, args=None)`

Execute a specific JavaScript file.

### `init_project(plugin_root, name="plugin-project")`

Initialize a new `package.json` in the plugin's `./pkg` directory.

## Environment Variables

The adapter automatically sets:
- `npm_config_prefix`: Points to the `./pkg` directory for isolated installs
- `NODE_PATH`: Points to `./pkg/node_modules` for module resolution

## Requirements

- Node.js (v14+) installed in the system PATH
- npm installed in the system PATH

## License

MIT
