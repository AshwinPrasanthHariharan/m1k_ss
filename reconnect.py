import time
from pathlib import Path

def reconnect(serial_number):
    sysfs_usb = Path('/sys/bus/usb/devices/')
    
    for device_path in sysfs_usb.iterdir():
        serial_file = device_path / 'serial'
        
        if serial_file.exists():
            try:
                # Strip standard whitespace AND null bytes
                current_serial = serial_file.read_text().strip().strip('\x00')
                
                if current_serial == serial_number:
                    authorized_file = device_path / 'authorized'
                    print(f"Match found at {device_path.name}.")
                    
                    try:
                        print("Simulating unplug...")
                        authorized_file.write_text('0\n')
                        time.sleep(2) 
                        
                        print("Simulating replug...")
                        authorized_file.write_text('1\n')
                        
                        print("Reconnect successful.")
                        return True
                    except PermissionError:
                        print(f"Error: You need udev rules to grant write access to {authorized_file}")
                        return False
                        
            except PermissionError:
                # If we can't even READ the serial file, let the user know instead of silently failing
                print(f"Warning: Permission denied reading serial for {device_path.name}")
            except Exception as e:
                print(f"Warning: Unexpected error reading {device_path.name}: {e}")
                
    print(f"Error: Could not find a USB device with serial '{serial_number}'.")
    return False

def reconnect_all(product_title="ADALM1000"):
    """Reconnect all USB devices matching the specified product title."""
    sysfs_usb = Path('/sys/bus/usb/devices/')
    reconnected_count = 0
    failed_count = 0
    
    print(f"Scanning for devices matching product '{product_title}'...")
    
    for device_path in sysfs_usb.iterdir():
        product_file = device_path / 'product'
        authorized_file = device_path / 'authorized'
        
        if product_file.exists() and authorized_file.exists():
            try:
                product_name = product_file.read_text().strip().strip('\x00')
                
                if product_title in product_name:
                    serial_file = device_path / 'serial'
                    serial = "unknown"
                    
                    if serial_file.exists():
                        try:
                            serial = serial_file.read_text().strip().strip('\x00')
                        except Exception:
                            pass
                    
                    print(f"\nFound: {product_name} (Serial: {serial}) at {device_path.name}")
                    
                    try:
                        print("  Simulating unplug...")
                        authorized_file.write_text('0\n')
                        time.sleep(2)
                        
                        print("  Simulating replug...")
                        authorized_file.write_text('1\n')
                        time.sleep(1)
                        
                        print("  Reconnect successful.")
                        reconnected_count += 1
                    except PermissionError:
                        print(f"  Error: Permission denied. You need udev rules to grant write access.")
                        failed_count += 1
                    except Exception as e:
                        print(f"  Error reconnecting: {e}")
                        failed_count += 1
                        
            except PermissionError:
                pass  # Skip devices we can't read
            except Exception as e:
                pass  # Skip devices with errors
    
    print(f"\n--- Reconnect All Summary ---")
    print(f"Successfully reconnected: {reconnected_count}")
    print(f"Failed: {failed_count}")
    
    if reconnected_count == 0:
        print(f"No devices matching '{product_title}' found.")
        return False
    
    return reconnected_count > 0

if __name__ == "__main__":
    # Reconnect specific device by serial number
    # reconnect("20322050544A4D392031303239303033")
    
    # Reconnect all ADALM1000 devices
    reconnect_all("ADALM1000")
