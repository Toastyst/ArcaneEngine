from config import CONFIG
from utils import setup_logging, log_info, log_error
from memory import Memory
from clipboard_watcher import ClipboardWatcher
from payload_parser import PayloadParser
from prompt_builder import PromptBuilder
from ollama_client import OllamaClient
from overlay import Overlay
from conversation_manager import ConversationManager
from data_providers.tsm_provider import TSMProvider
from rag.manager import RAGManager
import threading
import signal

stop_flag = threading.Event()

def make_input_handler(conv_manager, builder, client, memory, overlay):
    def handler(user_input):
        conv_manager.add_user(user_input)
        memory_data = memory.get('goals') or ''
        system_content = builder.build_lightweight_system(conv_manager.original_query, memory_data)
        messages = conv_manager.get_messages(system_content)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "Calculate basic math expressions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            }
        ]
        response = client.chat(messages, tools)
        conv_manager.add_assistant(response)
        overlay.append_response(user_input, response)
        log_info(f"Follow-up response: {response}")
    return handler

def watch_loop(watcher, parser, builder, client, overlay, memory, tsm_provider, rag_manager, conv_manager):
    while not stop_flag.is_set():
        try:
            payload = watcher.watch()
            log_info(f"Detected payload: {payload}")
            log_info("=== PROCESS START ===")
            data = parser.parse(payload)
            if data:
                if data.get('command') == 'market_status':
                    query = 'all'
                else:
                    query = data.get('query', data.get('command', ''))
                conv_manager.start_session(payload, query)
                memory_data = memory.get('goals') or ''
                # Get TSM data
                tsm_data = tsm_provider.get_data(query)
                log_info(f"TSM data loaded: {len(tsm_data) if isinstance(tsm_data, dict) else 'none'} items")
                if isinstance(tsm_data, dict):
                    rag_manager.upsert_data(tsm_data)
                    rag_chunks = rag_manager.retrieve(query)
                else:
                    rag_chunks = []
                log_info(f"RAG returned {len(rag_chunks)} chunks")
                system_content = builder.build_system(query, memory_data, rag_chunks)
                messages = conv_manager.get_messages(system_content)
                tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": "calculator",
                            "description": "Calculate basic math expressions",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "expression": {
                                        "type": "string"
                                    }
                                },
                                "required": ["expression"]
                            }
                        }
                    }
                ]
                response = client.chat(messages, tools)
                conv_manager.add_assistant(response)
                overlay.append_response(payload, response)
                overlay.enable_input()
                log_info(f"Response: {response}")
                log_info("=== PROCESS END ===")
            else:
                log_error("Failed to parse payload")
        except Exception as e:
            log_error(f"Error: {e}")

def main():
    print("Setting up logging...")
    setup_logging(CONFIG['log_file'])
    print("Logging setup done.")
    log_info("Starting Runtime Bridge")

    memory = Memory(CONFIG['memory_file'])
    watcher = ClipboardWatcher(CONFIG['clipboard_poll_interval'])
    parser = PayloadParser()
    builder = PromptBuilder()
    client = OllamaClient(CONFIG['ollama_model'])
    conv_manager = ConversationManager()
    overlay = Overlay(CONFIG['overlay_position'], CONFIG['overlay_size'], conv_manager=conv_manager, input_handler=None)
    input_handler = make_input_handler(conv_manager, builder, client, memory, overlay)
    overlay.input_handler = input_handler
    tsm_provider = TSMProvider(CONFIG)
    rag_manager = RAGManager(CONFIG)

    def signal_handler(sig, frame):
        stop_flag.set()
        overlay.root.quit()
        log_info("Shutting down Runtime Bridge")

    signal.signal(signal.SIGINT, signal_handler)

    # Run watcher in thread
    watcher_thread = threading.Thread(target=watch_loop, args=(watcher, parser, builder, client, overlay, memory, tsm_provider, rag_manager, conv_manager))
    watcher_thread.daemon = True
    watcher_thread.start()

    def check_stop():
        if stop_flag.is_set():
            overlay.root.quit()
        overlay.root.after(100, check_stop)

    overlay.root.after(100, check_stop)
    overlay.root.mainloop()
    log_info("Shutting down Runtime Bridge")

if __name__ == "__main__":
    main()
