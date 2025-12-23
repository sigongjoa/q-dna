const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const API_KEY = 'ctx7sk-0758bc10-91e6-4488-afdb-631aa5ed6fac';
const mcpServerPath = path.join(__dirname, 'node_modules', '.bin', 'context7-mcp');

const env = { ...process.env, CONTEXT7_API_KEY: API_KEY };

const server = spawn(mcpServerPath, [], {
    env,
    stdio: ['pipe', 'pipe', 'pipe']
});

let buffer = '';
let step = 0;
let fastapiId = '';
let sqlalchemyId = '';
const docsContent = [];

function sendLink(method, params, id) {
    server.stdin.write(JSON.stringify({ jsonrpc: "2.0", id, method, params }) + '\n');
}

server.stdout.on('data', (data) => {
    const chunk = data.toString();
    buffer += chunk;
    const lines = buffer.split('\n');
    buffer = lines.pop();

    for (const line of lines) {
        if (!line.trim()) continue;
        try {
            const msg = JSON.parse(line);

            // Step 0: Initialize
            if (step === 0 && msg.id === 1) {
                console.log('✅ Initialized. Resolving FastAPI...');
                sendLink('tools/call', { name: 'resolve-library-id', arguments: { query: 'fastapi' } }, 2);
                step = 1;
            }

            // Step 1: Resolved FastAPI ID -> Get Docs -> Resolve SQLAlchemy
            else if (step === 1 && msg.id === 2) {
                try { // Try parsing tool call result
                    const result = JSON.parse(msg.result.content[0].text);
                    fastapiId = result.libraryId; // Assuming result format { libraryId: "...", ... }
                    if (!fastapiId) fastapiId = "tiangolo/fastapi"; // Fallback if parsing varies
                } catch (e) { fastapiId = "tiangolo/fastapi"; } // Manual Fallback

                console.log(`✅ Resolved FastAPI: ${fastapiId}. Fetching docs...`);
                sendLink('tools/call', { name: 'get-library-docs', arguments: { context7CompatibleLibraryID: fastapiId, mode: 'code' } }, 3);
                step = 2;
            }

            // Step 2: Got FastAPI Docs -> Resolve SQLAlchemy
            else if (step === 2 && msg.id === 3) {
                docsContent.push(`# FastAPI Docs\n\n${msg.result.content[0].text}`);
                console.log('✅ Got FastAPI docs. Resolving SQLAlchemy...');
                sendLink('tools/call', { name: 'resolve-library-id', arguments: { query: 'sqlalchemy' } }, 4);
                step = 3;
            }

            // Step 3: Resolved SQLAlchemy -> Get Docs
            else if (step === 3 && msg.id === 4) {
                try {
                    const result = JSON.parse(msg.result.content[0].text);
                    sqlalchemyId = result.libraryId;
                    if (!sqlalchemyId) sqlalchemyId = "sqlalchemy/sqlalchemy";
                } catch (e) { sqlalchemyId = "sqlalchemy/sqlalchemy"; }

                console.log(`✅ Resolved SQLAlchemy: ${sqlalchemyId}. Fetching docs...`);
                sendLink('tools/call', { name: 'get-library-docs', arguments: { context7CompatibleLibraryID: sqlalchemyId, mode: 'code' } }, 5);
                step = 4;
            }

            // Step 4: Got SQLAlchemy Docs -> Finish
            else if (step === 4 && msg.id === 5) {
                docsContent.push(`# SQLAlchemy Docs\n\n${msg.result.content[0].text}`);
                console.log('✅ Got SQLAlchemy docs. Saving to file...');

                fs.writeFileSync('CONTEXT7_REFERENCES.md', docsContent.join('\n\n---\n\n'));
                console.log('🎉 Done! Saved to CONTEXT7_REFERENCES.md');

                server.kill();
                process.exit(0);
            }

        } catch (e) {
            // Ignore parse errors from non-json output or partial chunks
        }
    }
});

// Start
sendLink('initialize', {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "scaffolder", version: "1.0.0" }
}, 1);
