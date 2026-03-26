import py_compile
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

files = [
    'app.py',
    'config.py',
    'models.py',
    os.path.join('core','__init__.py'),
    os.path.join('core','gateway.py'),
    os.path.join('core','key_manager.py'),
    os.path.join('core','audit_logger.py'),
    os.path.join('core','encryption_engine.py'),
    os.path.join('core','protocol_adapter.py'),
    os.path.join('routes','__init__.py'),
    os.path.join('routes','auth.py'),
    os.path.join('routes','dashboard.py'),
    os.path.join('routes','gateway_api.py'),
    os.path.join('routes','keys.py'),
    os.path.join('routes','logs.py'),
    os.path.join('routes','settings.py'),
]

print("=== Syntax Check ===")
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print("OK: " + f)
    except py_compile.PyCompileError as e:
        print("SYNTAX ERROR: " + f + ": " + str(e))

print("")
print("=== Import Check ===")
try:
    from config import Config
    print("OK: config")
except Exception as e:
    print("IMPORT ERROR config: " + str(e))

try:
    from core.encryption_engine import EncryptionEngine
    print("OK: core.encryption_engine")
except Exception as e:
    print("IMPORT ERROR core.encryption_engine: " + str(e))

try:
    from core.protocol_adapter import ProtocolAdapter
    print("OK: core.protocol_adapter")
except Exception as e:
    print("IMPORT ERROR core.protocol_adapter: " + str(e))

try:
    from core.gateway import gateway, GatewayController
    print("OK: core.gateway")
except Exception as e:
    print("IMPORT ERROR core.gateway: " + str(e))

print("")
print("=== Flask App Check ===")
try:
    from app import create_app
    application = create_app()
    print("OK: Flask app created successfully")
except Exception as e:
    import traceback
    print("APP ERROR: " + str(e))
    traceback.print_exc()
