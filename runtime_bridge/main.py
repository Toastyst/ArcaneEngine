from config import CONFIG
from utils import setup_logging, log_info, log_error
from memory import Memory
from clipboard_watcher import ClipboardWatcher
from payload_parser import PayloadParser
from prompt_builder import PromptBuilder
from ollama_client import OllamaClient
from overlay import Overlay
import threading

stop_flag = threading.Event()

def watch_loop(watcher, parser, builder, client, overlay, memory):
    while not stop_flag.is_set():
        try:
            payload = watcher.watch()
            log_info(f"Detected payload: {payload}")
            data = parser.parse(payload)
            if data:
                query = data.get('query', '')
                memory_data = memory.get('goals') or ''
                prompt = builder.build(query, memory_data)
                response = client.call(prompt)
                overlay.show_response(response)
                log_info(f"Response: {response}")
            else:
                log_error("Failed to parse payload")
        except Exception as e:
            log_error(f"Error: {e}")

def main():
    setup_logging(CONFIG['log_file'])
    log_info("Starting Runtime Bridge")

    memory = Memory(CONFIG['memory_file'])
    watcher = ClipboardWatcher(CONFIG['clipboard_poll_interval'])
    parser = PayloadParser()
    builder = PromptBuilder()
    client = OllamaClient(CONFIG['ollama_model'])
    overlay = Overlay(CONFIG['overlay_position'], CONFIG['overlay_size'])

    # Run watcher in thread
    watcher_thread = threading.Thread(target=watch_loop, args=(watcher, parser, builder, client, overlay, memory))
    watcher_thread.daemon = True
    watcher_thread.start()

    try:
        overlay.run()  # Run overlay mainloop in main thread
    except KeyboardInterrupt:
        stop_flag.set()
        overlay.root.after(0, overlay.root.destroy)
        log_info("Shutting down Runtime Bridge")

if __name__ == "__main__":
    main()
