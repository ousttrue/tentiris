// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
'use strict';

import * as net from 'net';
import * as vscode from 'vscode';
import * as path from 'path';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient;

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    console.log('launch tentiris...');

    // const serverPath: string = context.asAbsolutePath(path.join("python", "tentiris", "server.py"));
    // const serverOptions: ServerOptions = { command: "python", args: [serverPath] };

    const serverOptions: ServerOptions = function () {
        return new Promise((resolve, reject) => {
            var client = new net.Socket();
            client.connect(32123, "127.0.0.1", function () {
                resolve({
                    reader: client,
                    writer: client
                });
            });
        });
    }

    const clientOptions: LanguageClientOptions = {
        documentSelector: [
            { scheme: "file", language: "markdown" }
        ],
        synchronize: {
            // Notify the server about file changes to '.clientrc files contained in the workspace
            fileEvents: vscode.workspace.createFileSystemWatcher('**/.clientrc')
        }
    };

    // Create the language client and start the client.
    client = new LanguageClient(
        'tentiris',
        'Tentiris Server',
        serverOptions,
        clientOptions
    );
    client.start();
}

// This method is called when your extension is deactivated
export function deactivate() { }
