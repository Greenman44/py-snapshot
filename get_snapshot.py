import gc
import json
import os
import sys
import time
import traceback
import threading
#This will later be set via CLI argument
OUTPUT_PATH = './snapshot.json'

def get_thread_info() -> list[dict]:
    """
    Retrieve information about all current threads including their stack traces.
    :return: List of dictionaries containing thread ID, name, and stack trace
    """
    frames = sys._current_frames()
    threads = []
    for thread_id, frame in frames.items():
        thread_name = None
        for t in threading.enumerate():
            if t.ident == thread_id:
                thread_name = t.name
                break
        stack = traceback.format_stack(frame)
        threads.append(
            {
                'thread_id': thread_id,
                'thread_name': thread_name or 'Unknown',
                'stack_trace': [line.rstrip() for line in stack]
            }
        )
        
    return threads

def get_object_stats(limit=20) -> dict:
    """
    Get statistics of the most common object types in memory.
    :param limit: Number of top object types to return
    :return: Dictionary with object type names as keys and their counts as values
    """
    gc.collect()
    obj_counts = {}
    for obj in gc.get_objects():
        t = type(obj).__name__
        obj_counts[t] = obj_counts.get(t, 0) + 1
    top = sorted(obj_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    return dict(top)

def get_loaded_modules() -> list[str]:
    """
    Get a sorted list of currently loaded module names.
    :return: Sorted list of module names
    """
    return sorted(sys.modules.keys())

def get_process_metadata() -> dict:
    """
    Get metadata about the current Python process.
    :return: Dictionary containing process metadata
    """
    return {
        'python_version': sys.version,
        'python_executable': sys.executable,
        'argv': sys.argv,
        'cwd': os.getcwd(),
        'platform': sys.platform,
        'pid': os.getpid(), 
    }

def main():
    try:
        sys.audit("cpython.remote_debugger_script", OUTPUT_PATH)

        data = {
            "timestamp": time.time(),
            "metadata": get_process_metadata(),
            "threads": get_thread_info(),
            "object_stats": get_object_stats(),
            "loaded_modules": get_loaded_modules(),
        }
        
        #This will be the output shown in cli. Later we could change output format via args
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
    except Exception as e:
        error_data = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        with open(OUTPUT_PATH + '.error', 'w', encoding='utf-8') as f:
            json.dump(error_data, f, indent=2)


if __name__ == "__main__":
    main()