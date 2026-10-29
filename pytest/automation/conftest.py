import os
import pytest
from device import Device

@pytest.fixture
def device():
    port = os.getenv("DEVICE_PORT")
    if not port:
        pytest.skip("Set DEVICE_PORT, e.g. COM5, /dev/ttyUSB0 or rfc2217://localhost:4000 (Wokwi)")
    dev = Device(port, timeout=1.0)

    try:
        response = dev.command("RESET")
        assert response.get("status") == "OK", (
            f"Precondition RESET failed: {response}"
        )

        yield dev

    finally:
        try:
            dev.command("RESET")
        finally:
            dev.close()
