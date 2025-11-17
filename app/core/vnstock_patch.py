"""
Patch để fix vnai Inspector issue trong vnstock 3.2.6
"""
import os
import sys

# Set environment variables
os.environ['VNSTOCK_DISABLE_TELEMETRY'] = '1'
os.environ['VNSTOCK_ID'] = 'VNSTOCK_API_USER'
os.environ['HOME'] = '/app'

# Create vnstock directory
vnstock_dir = os.path.expanduser('~/.vnstock')
os.makedirs(vnstock_dir, exist_ok=True)

# Monkey patch IPython.core.getipython để tránh lỗi trong vnai
try:
    import IPython.core.getipython

    # Mock get_ipython
    def mock_get_ipython():
        return None

    IPython.core.getipython.get_ipython = mock_get_ipython
except:
    pass

# Monkey patch vnai Inspector
def patch_vnai():
    try:
        import vnai.flow.relay as relay

        # Save original Inspector
        OriginalInspector = relay.Inspector

        class PatchedInspector(OriginalInspector):
            """Patched Inspector với home_dir fallback"""
            def __init__(self, *args, **kwargs):
                # Set home_dir trước khi gọi __init__ gốc
                self.home_dir = os.path.expanduser('~/.vnstock')
                os.makedirs(self.home_dir, exist_ok=True)
                try:
                    super().__init__(*args, **kwargs)
                except:
                    pass  # Ignore errors in parent init

        # Replace Inspector
        relay.Inspector = PatchedInspector
        print("✓ vnai Inspector patched successfully")

    except Exception as e:
        print(f"⚠ vnai patch warning: {e}")

# Apply patch
patch_vnai()
