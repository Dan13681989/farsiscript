const { createConnection, TextDocuments, DiagnosticSeverity } = require('vscode-languageserver/node');
const { TextDocument } = require('vscode-languageserver-textdocument');

const connection = createConnection();
const documents = new TextDocuments(TextDocument);

connection.onInitialize(() => ({ capabilities: { textDocumentSync: 1 } }));

async function validate(document) {
    const text = document.getText();
    const diagnostics = [];
    // Simple check for common errors
    if (text.includes('چاپ') && !text.includes(';')) {
        diagnostics.push({
            severity: DiagnosticSeverity.Warning,
            range: { start: { line: 0, character: 0 }, end: { line: 0, character: text.length } },
            message: 'Missing semicolon after print statement.',
            source: 'farsiscript'
        });
    }
    connection.sendDiagnostics({ uri: document.uri, diagnostics });
}

documents.onDidChangeContent(change => validate(change.document));
documents.listen(connection);
connection.listen();
