import time
import uuid
import asyncio
import lsprotocol.types as lsp_types
from pygls.server import LanguageServer

COUNT_DOWN_START_IN_SECONDS = 10
COUNT_DOWN_SLEEP_IN_SECONDS = 1

CONFIGURATION_SECTION = "Tentiris"


def count_down_10_seconds_blocking(ls: LanguageServer, *args):
    """Starts counting down and showing message synchronously.
    It will `block` the main thread, which can be tested by trying to show
    completion items.
    """
    for i in range(COUNT_DOWN_START_IN_SECONDS):
        ls.show_message(f"Counting down... {COUNT_DOWN_START_IN_SECONDS - i}")
        time.sleep(COUNT_DOWN_SLEEP_IN_SECONDS)


async def count_down_10_seconds_non_blocking(ls: LanguageServer, *args):
    """Starts counting down and showing message asynchronously.
    It won't `block` the main thread, which can be tested by trying to show
    completion items.
    """
    for i in range(COUNT_DOWN_START_IN_SECONDS):
        ls.show_message(f"Counting down... {COUNT_DOWN_START_IN_SECONDS - i}")
        await asyncio.sleep(COUNT_DOWN_SLEEP_IN_SECONDS)


async def progress(ls: LanguageServer, *args):
    """Create and start the progress on the client."""
    token = "token"
    # Create
    await ls.progress.create_async(token)
    # Begin
    ls.progress.begin(
        token, lsp_types.WorkDoneProgressBegin(title="Indexing", percentage=0)
    )
    # Report
    for i in range(1, 10):
        ls.progress.report(
            token,
            lsp_types.WorkDoneProgressReport(message=f"{i * 10}%", percentage=i * 10),
        )
        await asyncio.sleep(2)
    # End
    ls.progress.end(token, lsp_types.WorkDoneProgressEnd(message="Finished"))


async def register_completions(ls: LanguageServer, *args):
    """Register completions method on the client."""
    params = lsp_types.RegistrationParams(
        registrations=[
            lsp_types.Registration(
                id=str(uuid.uuid4()),
                method=lsp_types.TEXT_DOCUMENT_COMPLETION,
                register_options={"triggerCharacters": "[':']"},
            )
        ]
    )
    response = await ls.register_capability_async(params)
    if response is None:
        ls.show_message("Successfully registered completions method")
    else:
        ls.show_message(
            "Error happened during completions registration.",
            lsp_types.MessageType.Error,
        )


async def show_configuration_async(ls: LanguageServer, *args):
    """Gets exampleConfiguration from the client settings using coroutines."""
    try:
        config = await ls.get_configuration_async(
            lsp_types.ConfigurationParams(
                items=[
                    lsp_types.ConfigurationItem(
                        scope_uri="", section=CONFIGURATION_SECTION
                    )
                ]
            )
        )

        example_config = config[0].get("exampleConfiguration")

        ls.show_message(f"jsonServer.exampleConfiguration value: {example_config}")

    except Exception as e:
        ls.show_message_log(f"Error ocurred: {e}")


def show_configuration_callback(ls: LanguageServer, *args):
    """Gets exampleConfiguration from the client settings using callback."""

    def _config_callback(config):
        try:
            example_config = config[0].get("exampleConfiguration")

            ls.show_message(f"jsonServer.exampleConfiguration value: {example_config}")

        except Exception as e:
            ls.show_message_log(f"Error ocurred: {e}")

    ls.get_configuration(
        lsp_types.ConfigurationParams(
            items=[
                lsp_types.ConfigurationItem(scope_uri="", section=CONFIGURATION_SECTION)
            ]
        ),
        _config_callback,
    )


def show_configuration_thread(ls: LanguageServer, *args):
    """Gets exampleConfiguration from the client settings using thread pool."""
    try:
        config = ls.get_configuration(
            lsp_types.ConfigurationParams(
                items=[
                    lsp_types.ConfigurationItem(
                        scope_uri="", section=CONFIGURATION_SECTION
                    )
                ]
            )
        ).result(2)

        example_config = config[0].get("exampleConfiguration")

        ls.show_message(f"jsonServer.exampleConfiguration value: {example_config}")

    except Exception as e:
        ls.show_message_log(f"Error ocurred: {e}")


async def unregister_completions(ls: LanguageServer, *args):
    """Unregister completions method on the client."""
    params = lsp_types.UnregistrationParams(
        unregisterations=[
            lsp_types.Unregistration(
                id=str(uuid.uuid4()), method=lsp_types.TEXT_DOCUMENT_COMPLETION
            )
        ]
    )
    response = await ls.unregister_capability_async(params)
    if response is None:
        ls.show_message("Successfully unregistered completions method")
    else:
        ls.show_message(
            "Error happened during completions unregistration.",
            lsp_types.MessageType.Error,
        )
