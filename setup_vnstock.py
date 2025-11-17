"""
Script để setup vnstock và chấp nhận terms
"""
import os
import sys

def setup_vnstock():
    """Setup vnstock và chấp nhận điều khoản"""
    try:
        # Set environment variable để bypass terms
        os.environ['VNSTOCK_ID'] = 'VNSTOCK_USER'

        # Import và setup vnstock
        from vnstock import Vnstock
        print("✓ Vnstock đã được setup thành công!")
        return True
    except SystemExit as e:
        if 'điều khoản' in str(e):
            print("Attempting to accept terms...")
            try:
                # Try to create config file to accept terms
                from vnstock.core.utils.env import id_config
                id_config()
                print("✓ Terms accepted!")
                return True
            except:
                pass
        print(f"✗ Lỗi: {e}")
        return False
    except Exception as e:
        print(f"✗ Lỗi khi setup vnstock: {e}")
        return False

if __name__ == "__main__":
    success = setup_vnstock()
    sys.exit(0 if success else 1)
