// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
'use strict';

import * as net from "net";
import * as path from "path";
import { ExtensionContext, ExtensionMode, workspace } from "vscode";
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
} from "vscode-languageclient/node";

let client: LanguageClient;

function getClientOptions(): LanguageClientOptions {
    return {
        // Register the server for plain text documents
        documentSelector: [
            { scheme: "file", language: "json" },
            { scheme: "untitled", language: "json" },
        ],
        outputChannelName: "[pygls] JsonLanguageServer",
        synchronize: {
            // Notify the server about file changes to '.clientrc files contain in the workspace
            fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
        },
    };
}

function startLangServerTCP(host: string, addr: number): LanguageClient {
    console.debug(`connect ${host}:${addr}`)
    const serverOptions: ServerOptions = () => {
        return new Promise((resolve /*, reject */) => {
            const clientSocket = new net.Socket();
            clientSocket.connect(addr, host, () => {
                resolve({
                    reader: clientSocket,
                    writer: clientSocket,
                });
            });
        });
    };

    return new LanguageClient(
        `tcp lang server (port ${addr})`,
        serverOptions,
        getClientOptions()
    );
}

function startLangServer(
    command: string,
    args: string[],
    cwd: string
): LanguageClient {
    const serverOptions: ServerOptions = {
        args,
        command,
        options: { cwd },
    };

    return new LanguageClient(command, serverOptions, getClientOptions());
}

export function activate(context: ExtensionContext): void {
    if (context.extensionMode === ExtensionMode.Development) {
        // Development - Run the server manually
        client = startLangServerTCP('localhost', 32123);
    } else {
        // Production - Client is going to run the server (for use within `.vsix` package)
        const cwd = path.join(__dirname, "..", "..", "python");
        const pythonPath = workspace
            .getConfiguration("python")
            .get<string>("pythonPath");

        if (!pythonPath) {
            throw new Error("`python.pythonPath` is not set");
        }

        client = startLangServer(pythonPath, ["-m", "tentiris"], cwd);
    }

    context.subscriptions.push(client.start());
}

export function deactivate(): Thenable<void> {
    return client ? client.stop() : Promise.resolve();
}
