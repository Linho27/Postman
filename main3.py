#!/usr/bin/env python3
# Main control system for plate management

from modules.switches import getSwitches, compareSwitches, didntChange
from modules.fan import check_temp
from modules.leds import startUp, ledsOff, indicateRightPos, warnOccupiedPos, warnWrongPos, rightPos
from modules.connection import getPos, isOccupied, togglePos
import time
import sys

def main():
    try:
        # Initialize system
        print("Starting plate management system...")
        startUp()  # Test LEDs
        
        # Start fan control in background
        import threading
        fan_thread = threading.Thread(target=check_temp, daemon=True)
        fan_thread.start()
        
        # Main loop
        previous_states = getSwitches()
        while True:
            # Check for plate insertion/removal
            current_states = getSwitches()
            changed_switches = compareSwitches(previous_states)
            
            if not didntChange(changed_switches):
                for switch_num in changed_switches:
                    pos = switch_num + 1  # Convert to 1-based position
                    
                    # Plate inserted (switch activated)
                    if current_states[switch_num] == 0:
                        print(f"Plate detected in position {pos}")
                        
                        # Simulate QR code reading (replace with actual reader)
                        plate_id = input(f"Enter plate ID for position {pos}: ").strip()
                        
                        if not plate_id:  # Invalid code
                            print("Invalid plate code!")
                            warnOccupiedPos(pos)
                            continue
                        
                        # Get correct position from API
                        correct_pos_str = getPos(plate_id)
                        try:
                            correct_pos = int(correct_pos_str)
                        except (ValueError, TypeError):
                            print(f"Error: {correct_pos_str}")
                            warnOccupiedPos(pos)
                            continue
                        
                        # Check if position is free
                        if isOccupied(pos):
                            print(f"Position {pos} is already occupied!")
                            warnOccupiedPos(pos)
                            continue
                        
                        # Show correct position if different
                        if pos != correct_pos:
                            print(f"Plate should be in position {correct_pos}")
                            indicateRightPos(correct_pos)
                            time.sleep(5)  # Give time to see the indication
                        
                        # Check final placement
                        time.sleep(2)  # Wait for possible movement
                        final_pos = getSwitches()[switch_num]
                        
                        if final_pos == 0:  # Plate still there
                            if pos == correct_pos:
                                print("Correct position!")
                                rightPos(pos)
                                togglePos(pos)  # Update API
                            else:
                                print("Wrong position!")
                                warnWrongPos(correct_pos, pos)
                                ledsOff()
                    
                    # Plate removed (switch deactivated)
                    else:
                        print(f"Plate removed from position {pos}")
                        togglePos(pos)  # Update API
                        ledsOff()
                
                previous_states = current_states
            
            time.sleep(0.1)  # Small delay to prevent CPU overload
    
    except KeyboardInterrupt:
        print("\nShutting down system...")
        ledsOff()
        GPIO.cleanup()
        sys.exit(0)

if __name__ == "__main__":
    main()