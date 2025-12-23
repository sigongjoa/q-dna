const { spawn } = require('child_process');
const path = require('path');

const API_KEY = 'ctx7sk-0758bc10-91e6-4488-afdb-631aa5ed6fac';
const mcpServerPath = path.join(__dirname, 'node_modules', '.bin', 'context7-mcp');

const env = {
    ...process.env,
    CONTEXT7_API_KEY: API_KEY
};

const server = spawn(mcpServerPath, [], {
    env,
    stdio: ['pipe', 'pipe', 'pipe']
});

let buffer = '';

server.stdout.on('data', (data) => {
    const chunk = data.toString();
    buffer += chunk;

    const lines = buffer.split('\n');
    buffer = lines.pop();

    for (const line of lines) {
        if (!line.trim()) continue;

        try {
            const msg = JSON.parse(line);

            // 1. 초기화 응답 처리
            if (msg.id === 1 && msg.result) {
                console.log('✅ Initialized. Fetching tools...');
                // 2. 툴 목록 요청
                const toolsRequest = {
                    jsonrpc: "2.0",
                    id: 2,
                    method: "tools/list"
                };
                server.stdin.write(JSON.stringify(toolsRequest) + '\n');
            }
            // 3. 툴 목록 응답 처리
            else if (msg.id === 2 && msg.result) {
                console.log('\n🛠️  Available Tools:');
                msg.result.tools.forEach(tool => {
                    console.log(`- ${tool.name}: ${tool.description}`);
                });

                // 툴 목록을 확인했으니 종료
                server.kill();
                process.exit(0);
            }
        } catch (e) {
            // JSON 파싱 에러는 무시 (로그 등)
        }
    }
});

// 초기화 요청 전송
const initRequest = {
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
        protocolVersion: "2024-11-05",
        capabilities: {},
        clientInfo: { name: "inspector", version: "1.0.0" }
    }
};

server.stdin.write(JSON.stringify(initRequest) + '\n');
