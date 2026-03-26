"""
Protocol Adaptation Layer — Detect, normalize, and convert data formats
for compatibility with legacy communication protocols.
"""

import base64
import json


class ProtocolAdapter:
    """Handles format detection and normalization for legacy protocols."""

    FORMATS = ['raw', 'hex', 'base64', 'json', 'ascii']

    @staticmethod
    def detect_format(data):
        """
        Detect the format of incoming data.

        Returns:
            str: one of 'hex', 'base64', 'json', 'ascii', 'raw'
        """
        if isinstance(data, bytes):
            try:
                text = data.decode('utf-8')
            except UnicodeDecodeError:
                return 'raw'
        else:
            text = data

        # Try JSON
        try:
            json.loads(text)
            return 'json'
        except (json.JSONDecodeError, TypeError):
            pass

        # Try hex
        stripped = text.strip()
        if stripped and all(c in '0123456789abcdefABCDEF' for c in stripped):
            return 'hex'

        # Try base64
        try:
            decoded = base64.b64decode(stripped, validate=True)
            if len(decoded) > 0 and len(stripped) > 4:
                return 'base64'
        except Exception:
            pass

        # Check if pure ASCII printable
        if all(32 <= ord(c) < 127 or c in '\n\r\t' for c in text):
            return 'ascii'

        return 'raw'

    @staticmethod
    def to_bytes(data, source_format=None):
        """
        Convert data from detected or specified format to bytes.

        Args:
            data: input data (str or bytes)
            source_format: optional format hint ('hex', 'base64', 'json', 'ascii', 'raw')

        Returns:
            bytes
        """
        if source_format is None:
            source_format = ProtocolAdapter.detect_format(data)

        if isinstance(data, bytes):
            if source_format == 'raw':
                return data
            data = data.decode('utf-8', errors='replace')

        if source_format == 'hex':
            return bytes.fromhex(data.strip())
        elif source_format == 'base64':
            return base64.b64decode(data.strip())
        elif source_format == 'json':
            return json.dumps(json.loads(data)).encode('utf-8')
        elif source_format in ('ascii', 'raw'):
            return data.encode('utf-8') if isinstance(data, str) else data
        else:
            return data.encode('utf-8') if isinstance(data, str) else data

    @staticmethod
    def from_bytes(data, target_format='ascii'):
        """
        Convert bytes to the specified target format.

        Args:
            data: bytes to convert
            target_format: 'hex', 'base64', 'json', 'ascii'

        Returns:
            str
        """
        if not isinstance(data, bytes):
            data = data.encode('utf-8') if isinstance(data, str) else bytes(data)

        if target_format == 'hex':
            return data.hex()
        elif target_format == 'base64':
            return base64.b64encode(data).decode('utf-8')
        elif target_format == 'json':
            try:
                return json.dumps(json.loads(data.decode('utf-8')))
            except Exception:
                return base64.b64encode(data).decode('utf-8')
        elif target_format == 'ascii':
            return data.decode('utf-8', errors='replace')
        else:
            return data.decode('utf-8', errors='replace')

    @staticmethod
    def normalize(data, source_format=None, target_format='ascii'):
        """
        Full normalization pipeline: detect → to_bytes → from_bytes.
        """
        if source_format is None:
            source_format = ProtocolAdapter.detect_format(data)

        raw = ProtocolAdapter.to_bytes(data, source_format)
        output = ProtocolAdapter.from_bytes(raw, target_format)

        return {
            'source_format': source_format,
            'target_format': target_format,
            'input_size': len(data) if isinstance(data, (str, bytes)) else 0,
            'output_size': len(output),
            'output': output
        }
