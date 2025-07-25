#!/usr/bin/env python3  
"""  
Start the Casbin Python API server 
"""  
import os  
import sys  
from api_server import app  
  
def main():  
    # Make sure the current directory is in the Python path  
    current_dir = os.path.dirname(os.path.abspath(__file__))  
    if current_dir not in sys.path:  
        sys.path.insert(0, current_dir)  
      
    # configuration  
    host = os.getenv('API_HOST', '127.0.0.1')
    port = int(os.getenv('API_PORT', 8080))  
    debug = os.getenv('API_DEBUG', 'true').lower() == 'true'  
      
    print(f" Starting Casbin Python API server...")  
    print(f" Server: http://{host}:{port}")  
    print(f" Debug mode: {debug}")  
    print(f" Working directory: {current_dir}")  
      
    app.run(host=host, port=port, debug=debug)  
  
if __name__ == '__main__':  
    main()