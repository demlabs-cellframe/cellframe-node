const vscode = require('vscode');

function activate(context) {
    console.log('Cellframe API Documentation extension activated');
    
    let disposable = vscode.commands.registerCommand('cellframe.searchAPI', function () {
        vscode.window.showInformationMessage('Cellframe API Search - Coming Soon!');
    });
    
    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
}