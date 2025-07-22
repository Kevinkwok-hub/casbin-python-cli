import os    
import sys    
import subprocess    
import platform    
import argparse  
    
def build_binary():    
    """Build standalone binary using PyInstaller"""  
      
    # Parse command line arguments (保持兼容性)  
    parser = argparse.ArgumentParser()  
    parser.add_argument('--platform', help='Target platform (linux, darwin, windows)')  
    args = parser.parse_args()  
        
    # Install PyInstaller if not present    
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)    
        
    # Get platform info    
    system = platform.system().lower()    
    arch = platform.machine().lower()  
      
    # 标准化架构名称  
    arch_mapping = {  
        'x86_64': 'x86_64',  
        'amd64': 'x86_64',   
        'arm64': 'arm64',  
        'aarch64': 'arm64',  
        'i386': '386',  
        'i686': '386'  
    }  
      
    normalized_arch = arch_mapping.get(arch, arch)  
      
    # 如果提供了platform参数，使用它；否则使用自动检测  
    if args.platform:  
        if args.platform == 'darwin':  
            system = 'darwin'  
        elif args.platform == 'linux':  
            system = 'linux'  
        elif args.platform == 'windows':  
            system = 'windows'  
        
    # Build binary name - 确保格式正确  
    binary_name = f"casbin-python-cli-{system}-{normalized_arch}"  
    executable_name = binary_name  
    if system == "windows":    
        executable_name += ".exe"  
        
    cmd = [    
        "pyinstaller",    
        "--onefile",    
        "--name", binary_name,  # 不包含.exe，PyInstaller会自动添加  
        "--console",    
        "--paths", ".",    
        "--hidden-import", "casbin_cli",    
        "--hidden-import", "casbin",    
        "--hidden-import", "casbin_cli.client",    
        "--hidden-import", "casbin_cli.command_executor",     
        "--hidden-import", "casbin_cli.enforcer_factory",    
        "--hidden-import", "casbin_cli.response",    
        "--hidden-import", "casbin_cli.utils",    
        "--collect-all", "casbin",   
        "casbin_cli/client.py"    
    ]   
        
    subprocess.run(cmd, check=True)    
        
    print(f"Binary built successfully: dist/{executable_name}")    
    
if __name__ == "__main__":    
    build_binary()