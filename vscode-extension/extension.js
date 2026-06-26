const vscode = require('vscode');
const { LanguageClient } = require('vscode-languageclient/node');

let client;

function activate(context) {
    const serverModule = context.asAbsolutePath('server.js');
    const serverOptions = {
        run: { command: 'node', args: [serverModule] },
        debug: { command: 'node', args: [serverModule] }
    };
    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'farsiscript' }]
    };
    client = new LanguageClient('farsiscript', 'FarsiScript Language Server', serverOptions, clientOptions);
    client.start();
}

function deactivate() {
    if (client) client.stop();
}

module.exports = { activate, deactivate };
