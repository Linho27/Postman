# switches.py - Complete Switch Management Module
import RPi.GPIO as GPIO
import time
from typing import List, Dict, Optional
from modules.connection import togglePos, isOccupied

# GPIO Pin Configuration (BCM numbering)
switches_pins = [4, 5, 6, 12, 13, 16, 20, 21, 22, 23, 24, 25]  # Positions 1-12

class SwitchManager:
    def _init_(self):
        """Initialize switch manager with GPIO setup"""
        GPIO.setmode(GPIO.BCM)
        self.position_status = [False] * 12  # Tracks physical switch states
        self.api_sync_time = time.time()
        self._setup_gpio()
    
    def _setup_gpio(self):
        """Configure GPIO pins as inputs with pull-up resistors"""
        for pin in switches_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    def syncSwitchesWithAPI(self, force: bool = False) -> Dict[int, str]:
        """
        Synchronize all switch states with API
        Args:
            force: If True, sync all positions regardless of state
        Returns:
            Dictionary with sync results {position: status_message}
        """
        results = {}
        self.update_positions()
        
        for position in range(1, 13):  # Positions 1-12
            physical_state = self.position_status[position-1]
            api_state = isOccupied(position)
            
            # Only sync if states differ or forced
            if force or (physical_state != api_state):
                result = togglePos(position)
                results[position] = f"Physical: {physical_state} | API: {api_state} | {result}"
                
        self.api_sync_time = time.time()
        return results
    
    def update_positions(self) -> Dict[int, bool]:
        """Update and return current positions status"""
        for i, pin in enumerate(switches_pins):
            self.position_status[i] = GPIO.input(pin) == GPIO.LOW
        return {pos+1: status for pos, status in enumerate(self.position_status)}
    
    def get_position_status(self, position: int) -> bool:
        """Get status of specific position (1-12)"""
        if 1 <= position <= 12:
            return self.position_status[position-1]
        raise ValueError("Position must be between 1-12")
    
    def get_occupied_positions(self) -> List[int]:
        """List all currently occupied positions"""
        return [pos+1 for pos, status in enumerate(self.position_status) if status]
    
    def wait_for_change(self, timeout: float = 30.0) -> Optional[int]:
        """
        Wait for any switch state change
        Args:
            timeout: Maximum wait time in seconds
        Returns:
            Position that changed (1-12) or None if timeout
        """
        start = time.time()
        last_states = self.position_status.copy()
        
        while (time.time() - start) < timeout:
            self.update_positions()
            for pos in range(12):
                if self.position_status[pos] != last_states[pos]:
                    return pos + 1  # Return position (1-12)
            time.sleep(0.1)
        
        return None
    
    def monitor_switches(self, callback=None, interval: float = 0.5):
        """
        Continuously monitor switches and trigger callback on changes
        Args:
            callback: Function to call when changes detected
            interval: Check interval in seconds
        """
        try:
            while True:
                changed = self.update_positions()
                if callback:
                    callback(changed)
                time.sleep(interval)
        except KeyboardInterrupt:
            pass

    def cleanup(self):
        """Clean up GPIO resources"""
        GPIO.cleanup()

# Global instance for easy access
switch_manager = SwitchManager()

# Legacy functions for backward compatibility
def getSwitches() -> List[int]:
    """Get raw switch states (0/1) for all pins"""
    return [GPIO.input(pin) for pin in switches_pins]

def compareSwitches(old_states: List[int]) -> List[int]:
    """Compare current states with previous states"""
    current = getSwitches()
    return [i for i in range(12) if current[i] != old_states[i]]

def didntChange(states: List[int]) -> bool:
    """Check if states remain unchanged"""
    return len(states) == 0

def update_positions() -> Dict[int, bool]:
    """Legacy function to update positions"""
    return switch_manager.update_positions()