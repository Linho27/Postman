# switches.py - Complete Switch Management Module with API Sync
import RPi.GPIO as GPIO
import time
import logging
from typing import List, Dict, Optional, Tuple
from modules.connection import togglePos, isOccupied

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardware Configuration
SWITCHES_PINS = {
    1: 2,   2: 3,   3: 4,    4: 17,
    5: 27,  6: 22,  7: 10,   8: 9,
    9: 11, 10: 5,  11: 6,   12: 13
}  # {position: BCM_pin}

class SwitchManager:
    _gpio_initialized = False

    def _init_(self):
        self._initialize_gpio()
        self.position_states = {pos: False for pos in SWITCHES_PINS}
        self.last_sync_time = 0
        self.debounce_time = 0.1  # seconds

    def _initialize_gpio(self):
        """Safe one-time GPIO initialization"""
        if not SwitchManager._gpio_initialized:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                for pin in SWITCHES_PINS.values():
                    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                SwitchManager._gpio_initialized = True
                logger.info("GPIO initialized successfully")
            except Exception as e:
                logger.error(f"GPIO init failed: {str(e)}")
                raise

    def syncSwitchesWithAPI(self, force: bool = False) -> Dict[int, Tuple[bool, str]]:
        """
        Synchronize all switch states with API
        Args:
            force: Sync all positions regardless of current state
        Returns:
            {position: (success, message)}
        """
        results = {}
        self.read_physical_states()
        
        for position, pin in SWITCHES_PINS.items():
            try:
                physical_state = self.position_states[position]
                api_state = isOccupied(position)
                
                if force or (physical_state != api_state):
                    response = togglePos(position)
                    success = "sucesso" in response.lower() or "success" in response.lower()
                    results[position] = (success, response)
                    if success:
                        logger.info(f"Pos {position} sync: Physical {physical_state} → API {not api_state}")
            except Exception as e:
                results[position] = (False, f"Error: {str(e)}")
                logger.error(f"Sync failed for pos {position}: {str(e)}")
        
        self.last_sync_time = time.time()
        return results

    def read_physical_states(self) -> Dict[int, bool]:
        """Read all switch states with debounce"""
        time.sleep(self.debounce_time)
        for position, pin in SWITCHES_PINS.items():
            try:
                self.position_states[position] = GPIO.input(pin) == GPIO.LOW
            except Exception as e:
                logger.error(f"Read failed for pos {position}: {str(e)}")
        return self.position_states.copy()

    def get_state(self, position: int) -> Optional[bool]:
        """Get current state of a single switch"""
        if position not in SWITCHES_PINS:
            logger.error(f"Invalid position {position}")
            return None
        return self.position_states.get(position)

    def wait_for_change(self, timeout: float = 30.0) -> Optional[int]:
        """Wait for any switch state change"""
        start_time = time.time()
        initial_states = self.read_physical_states()
        
        while time.time() - start_time < timeout:
            current_states = self.read_physical_states()
            for position in SWITCHES_PINS:
                if current_states[position] != initial_states[position]:
                    logger.info(f"Position {position} changed to {current_states[position]}")
                    return position
            time.sleep(0.05)
        
        logger.warning("Switch change detection timeout")
        return None

    def monitor_changes(self, callback, interval: float = 0.1):
        """Monitor switches continuously"""
        try:
            last_states = self.read_physical_states()
            while True:
                current_states = self.read_physical_states()
                for pos in SWITCHES_PINS:
                    if current_states[pos] != last_states[pos]:
                        callback(pos, current_states[pos])
                last_states = current_states
                time.sleep(interval)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            logger.error(f"Monitoring failed: {str(e)}")

    def cleanup(self):
        """Clean up GPIO resources safely"""
        if SwitchManager._gpio_initialized:
            try:
                GPIO.cleanup()
                SwitchManager._gpio_initialized = False
                logger.info("GPIO cleanup completed")
            except Exception as e:
                logger.error(f"Cleanup failed: {str(e)}")

# Singleton instance
switch_manager = SwitchManager()

# Legacy functions
def getSwitches() -> List[int]:
    """Legacy: Get raw states for all switches"""
    return [GPIO.input(pin) for pin in SWITCHES_PINS.values()]

def compareSwitches(old_states: List[int]) -> List[int]:
    """Legacy: Compare with previous states"""
    current = getSwitches()
    return [i for i, (old, new) in enumerate(zip(old_states, current)) if old != new]

def didntChange(states: List[int]) -> bool:
    """Legacy: Check if no changes"""
    return len(states) == 0

def update_positions() -> Dict[int, bool]:
    """Legacy: Update and get all states"""
    return switch_manager.read_physical_states()