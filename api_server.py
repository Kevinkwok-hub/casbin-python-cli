from flask import Flask, request, jsonify  
import subprocess  
import json  
import hashlib  
from datetime import datetime  
import os  
import sys  
import ssl  
from OpenSSL import SSL, crypto  
  
app = Flask(__name__)  
  
def generate_self_signed_cert():  
    """Generate self-signed certificate for development environment"""  
    # Create certificate directory  
    cert_dir = os.path.join(os.path.dirname(__file__), 'certs')  
    os.makedirs(cert_dir, exist_ok=True)  
      
    cert_file = os.path.join(cert_dir, 'cert.pem')  
    key_file = os.path.join(cert_dir, 'key.pem')  
      
    # Return existing certificate if found  
    if os.path.exists(cert_file) and os.path.exists(key_file):  
        return cert_file, key_file  
      
    # Create key pair  
    key = crypto.PKey()  
    key.generate_key(crypto.TYPE_RSA, 2048)  
      
    # Create certificate  
    cert = crypto.X509()  
    cert.get_subject().C = "US"  
    cert.get_subject().ST = "State"  
    cert.get_subject().L = "City"  
    cert.get_subject().O = "Organization"  
    cert.get_subject().OU = "Organizational Unit"  
    cert.get_subject().CN = "localhost"  
      
    # Add Subject Alternative Names  
    cert.add_extensions([  
        crypto.X509Extension(b"subjectAltName", False, b"DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1"),  
    ])  
      
    cert.set_serial_number(1000)  
    cert.gmtime_adj_notBefore(0)  
    cert.gmtime_adj_notAfter(365*24*60*60)  # 1 year validity  
    cert.set_issuer(cert.get_subject())  
    cert.set_pubkey(key)  
    cert.sign(key, 'sha256')  
      
    # Save certificate and key  
    with open(cert_file, 'wb') as f:  
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))  
      
    with open(key_file, 'wb') as f:  
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))  
      
    print(f" Self-signed certificate generated: {cert_file}")  
    print(f" Private key generated: {key_file}")  
      
    return cert_file, key_file  
  
def generate_identifier_param(params=None):  
    """Generate SHA-256 hash authentication parameters"""  
    if params is None:  
        params = {}  
      
    timestamp = datetime.utcnow().isoformat() + 'Z'  
    version = 'casbin-editor-v1'  
      
    raw_string = f"{version}|{timestamp}"  
      
    if params:  
        sorted_params = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))  
        raw_string = f"{raw_string}|{sorted_params}"  
      
    hash_obj = hashlib.sha256(raw_string.encode('utf-8'))  
    hash_hex = hash_obj.hexdigest()  
      
    return hash_hex, timestamp  
  
def verify_hash(params, provided_hash, timestamp):  
    """Verify request hash"""  
    expected_hash, _ = generate_identifier_param(params)  
    return expected_hash == provided_hash  
  
@app.route('/api/run-casbin-command', methods=['GET'])  
def run_casbin_command():  
    """Handle Casbin command execution requests"""  
    try:  
        # Get request parameters  
        language = request.args.get('language')  
        args_json = request.args.get('args')  
        hash_param = request.args.get('m')  
        timestamp = request.args.get('t')  
          
        print(f"🔍 Received request: language={language}, args={args_json}")  
          
        # Handle unsupported languages gracefully  
        if language != 'python':  
            print(f" Unsupported language: {language}, returning mock version info")  
            # Return mock version info that matches expected format  
            return jsonify({  
                "status": "ok",  
                "data": "CLI version: unavailable\nLibrary version: unavailable"  
            }), 200  
          
        if not args_json:  
            return jsonify({  
                "status": "error",   
                "msg": "Missing args parameter"  
            }), 400  
          
        # Parse command arguments  
        try:  
            args = json.loads(args_json)  
            print(f" Parsed arguments: {args}")  
        except json.JSONDecodeError as e:  
            return jsonify({  
                "status": "error",   
                "msg": f"Invalid JSON in args: {str(e)}"  
            }), 400  
          
        # Optional: verify hash (if security authentication is needed)
        
        if hash_param and timestamp:  
            params = {'language': language, 'args': args_json}  
            if not verify_hash(params, hash_param, timestamp):  
                print(" Hash verification failed")  
                return jsonify({  
                    "status": "error",   
                    "msg": "Invalid authentication hash"  
                }), 401  
            
        # Build CLI command  
        # Use current Python interpreter and module path  
        cli_command = [sys.executable, '-m', 'casbin_cli.client'] + args  
        print(f"🚀 Executing command: {' '.join(cli_command)}")  
          
        # Set working directory to current directory  
        current_dir = os.path.dirname(os.path.abspath(__file__))  
          
        # Execute CLI command  
        result = subprocess.run(  
            cli_command,   
            capture_output=True,   
            text=True,   
            cwd=current_dir,  
            timeout=30  # 30 second timeout  
        )  
          
        print(f" Command return code: {result.returncode}")  
        print(f" Standard output: {result.stdout}")  
        if result.stderr:  
            print(f" Standard error: {result.stderr}")  
          
        if result.returncode == 0:  
            return jsonify({  
                "status": "ok",  
                "data": result.stdout.strip()  
            })  
        else:  
            return jsonify({  
                "status": "error",   
                "msg": result.stderr.strip() or "Command execution failed"  
            }), 500  
              
    except subprocess.TimeoutExpired:  
        print(" Command execution timeout")  
        return jsonify({  
            "status": "error",  
            "msg": "Command execution timeout"  
        }), 500  
    except Exception as e:  
        print(f" Internal server error: {str(e)}")  
        return jsonify({  
            "status": "error",  
            "msg": f"Internal server error: {str(e)}"  
        }), 500  
  
@app.route('/api/refresh-engines', methods=['POST'])  
def refresh_engines():  
    """Refresh engine status (optional endpoint)"""  
    return jsonify({  
        "status": "ok",  
        "data": "Python engine refreshed"  
    })  
  
@app.route('/health', methods=['GET'])  
def health_check():  
    """Health check endpoint"""  
    return jsonify({  
        "status": "ok",  
        "service": "casbin-python-api",  
        "timestamp": datetime.utcnow().isoformat()  
    })  
  
@app.after_request  
def after_request(response):  
    """Add CORS headers"""  
    response.headers.add('Access-Control-Allow-Origin', '*')  
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')  
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')  
    return response  
  
if __name__ == '__main__':  
    # Get configuration from environment variables  
    host = os.getenv('API_HOST', '127.0.0.1')  
    port = int(os.getenv('API_PORT', 8080))  
    debug = os.getenv('API_DEBUG', 'true').lower() == 'true'  
    use_https = os.getenv('USE_HTTPS', 'true').lower() == 'true'  
      
    print(f" Starting Casbin Python API server...")  
    print(f" Host: {host}")  
    print(f" Port: {port}")  
    print(f" Debug mode: {debug}")  
    print(f" HTTPS: {use_https}")  
      
    if use_https:  
        try:  
            # Try to import pyOpenSSL  
            import OpenSSL  
              
            # Generate or use existing self-signed certificate  
            cert_file, key_file = generate_self_signed_cert()  
              
            # Create SSL context  
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)  
            context.load_cert_chain(cert_file, key_file)  
              
            print(f" Using HTTPS, certificate: {cert_file}")  
            print(f" Server address: https://{host}:{port}")  
            print("  Note: Using self-signed certificate, browser may show security warning")  
              
            app.run(host=host, port=port, debug=debug, ssl_context=context)  
              
        except ImportError:  
            print(" Missing pyOpenSSL dependency, please install: pip install pyOpenSSL")  
            print(" Falling back to HTTP mode...")  
            print(f" Server address: http://{host}:{port}")  
            app.run(host=host, port=port, debug=debug)  
        except Exception as e:  
            print(f" HTTPS startup failed: {str(e)}")  
            print(" Falling back to HTTP mode...")  
            print(f" Server address: http://{host}:{port}")  
            app.run(host=host, port=port, debug=debug)  
    else:  
        print(f" Server address: http://{host}:{port}")  
        app.run(host=host, port=port, debug=debug)