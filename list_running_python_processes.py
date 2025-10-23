
import os
import psutil
def is_python_process(proc: psutil.Process) -> bool:
    """
    Check if a given process is a Python process.
    :param proc: psutil.Process object
    :return: True if the process is a Python process, False otherwise
    """
    try:
        exe = proc.exe().lower()
        if not exe:
            return False
        basename = os.path.basename(exe).lower()
        
        return any(basename.startswith(prefix) for prefix in ['python', 'pypy'])
        
    
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def get_python_version(cmdline:list[str]) -> str:
    """
    Extract the Python version from the command line arguments.
    :param cmdline: List of command line arguments
    :return: Python version string if found, else 'unknown'
    """
    if not cmdline:
        return 'unknown'
    exe = os.path.basename(cmdline[0]).lower()
    if exe.startswith('python'):
        #Try to extract version from executable name e.g., python3.12
        ver_part = exe.replace('python', '').replace('.exe', '')
        if ver_part and ver_part[0].isdigit():
            return ver_part
    return 'unknown'
        
    

def main():
    """
    List all running Python processes on the system. Only processes that we have permission to access will be displayed.
    """
    print(f"{'NAME':<10} {'PID':<8} {'VERSION':<10} {'MEM%':<6} {'CMD'}")
    print("-" * 60)
    for proc in psutil.process_iter(attrs=['pid', 'exe', 'name', 'cmdline', 'memory_percent']):
        try:
            if not is_python_process(proc):
                continue
            name = proc.info['name'] or ''
            pid = proc.info['pid']
            cmdline = proc.info['cmdline'] or []
            mem_percent = proc.info['memory_percent']
            cmd = ' '.join(cmdline[:4])+('...' if len(cmdline) > 4 else '')
            
            
        except(psutil.NoSuchProcess, psutil.AccessDenied):
            continue


if __name__ == "__main__":
    main()