const { spawn } = require('child_process');
const path = require('path');

// API Key configuration
const API_KEY = 'ctx7sk-0758bc10-91e6-4488-afdb-631aa5ed6fac';

// Path to the executable
const mcpServerPath = path.join(__dirname, 'node_modules', '.bin', 'context7-mcp');

console.log(`Starting Context7 MCP Server from: ${mcpServerPath}`);

const env = {
    ...process.env,
    CONTEXT7_API_KEY: API_KEY,
    // Some MCP servers might look for different env vars, but standard is usually this or via args.
    // We will assume env var as primarily suggested.
};

const server = spawn(mcpServerPath, [], {
    env,
    stdio: ['pipe', 'pipe', 'pipe']
});

let isInitialized = false;

// Buffer to handle split chunks
let buffer = '';

server.stdout.on('data', (data) => {
    const chunk = data.toString();
    buffer += chunk;

    // Process complete messages separated by newlines
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep the last incomplete part

    for (const line of lines) {
        if (!line.trim()) continue;

        console.log('[MCP Server Response]:', line);

        try {
            const response = JSON.parse(line);
            if (response.id === 1 && response.result) {
                console.log('✅ Initialization successful!');
                console.log('Server Capabilities:', JSON.stringify(response.result.capabilities, null, 2));
                isInitialized = true;

                // Clean exit after success
                server.kill();
                process.exit(0);
            }
        } catch (e) {
            console.error('Error parsing JSON:', e);
        }
    }
});

server.stderr.on('data', (data) => {
    console.error('[MCP Server Error]:', data.toString());
});

server.on('close', (code) => {
    console.log(`MCP Server exited with code ${code}`);
    if (!isInitialized) {
        console.error('❌ Failed to verify connection.');
        process.exit(1);
    }
});

// Send Initialize Request
// MCP Protocol: https://github.com/model-context-protocol/specification
const initRequest = {
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
        protocolVersion: "2024-11-05", // Specifying a recent version
        capabilities: {},
        clientInfo: {
            name: "verification-script",
            version: "1.0.0"
        }
    }
};

console.log('Sending Initialize Request...');
server.stdin.write(JSON.stringify(initRequest) + '\n');
