import pytest

def test_ping(device):
    r = device.command("PING")
    assert r["status"] == "OK"
    assert r["command"] == "PING"

def test_status(device):
    r = device.command("STATUS")
    assert r["status"] == "OK"
    assert "heap" in r
    assert "pwm" in r

def test_temperature_is_valid_json(device):
    r = device.command("GET TEMP")
    assert r["status"] in {"OK", "ERROR"}
    if r["status"] == "OK":
        assert -40 <= r["temperature"] <= 80

def test_led_on_off(device):
    assert device.command("SET LED ON")["led"] is True
    assert device.command("SET LED OFF")["led"] is False

def test_reset_restores_safe_state(device):
    device.command("SET LED ON")
    device.command("RESET")
    status = device.command("STATUS")
    assert status["pwm"] == 0
    assert status["led"] is False

def test_unknown_command(device):
    r = device.command("PONG")
    assert r["status"] == "ERROR"
    assert r["code"] == "UNKNOWN_COMMAND"

@pytest.mark.parametrize("value", [0, 1, 50, 99, 100])
def test_pwm_valid_boundaries(device, value):
    r = device.command(f"SET PWM {value}")
    assert r["status"] == "OK"
    assert r["pwm"] == value

@pytest.mark.parametrize("value", [-1, 101, 999])
def test_pwm_invalid_boundaries(device, value):
    r = device.command(f"SET PWM {value}")
    assert r["status"] == "ERROR"
    assert r["code"] == "INVALID_VALUE"

@pytest.mark.parametrize("value", [15, 75, 98])
def test_pwm__additional_valid_boundaries(device, value):
    r = device.command(f"SET PWM {value}")
    assert r["status"] == "OK"
    assert r["pwm"] == value

@pytest.mark.parametrize("value", [-101, -10, ])
def test_pwm_additional_invalid_boundaries(device, value):
    r = device.command(f"SET PWM {value}")
    assert r["status"] == "ERROR"
    assert r["code"] == "INVALID_VALUE"

