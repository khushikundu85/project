import os
from scanner import scanner

def test_scanner_safe():
    content = b"This is a safe text file with no malicious patterns."
    result = scanner.scan(content, "test.txt")
    print(f"Safe Test: {result['status']} (Risk: {result['risk_score']})")
    assert result['status'] == "Safe"

def test_scanner_malicious():
    content = b"import os; os.system('rm -rf /'); eval('dangerous'); exec('payload')"
    result = scanner.scan(content, "malicious.py")
    print(f"Malicious Test: {result['status']} (Risk: {result['risk_score']})")
    assert result['status'] == "Suspicious"

def test_scanner_executable():
    content = b"MZ\x90\x00\x03\x00\x00\x00" # Simple EXE header
    result = scanner.scan(content, "virus.exe")
    print(f"Executable Test: {result['status']} (Risk: {result['risk_score']})")
    assert result['risk_score'] >= 0.5

if __name__ == "__main__":
    print("Running Scanner Tests...")
    try:
        test_scanner_safe()
        test_scanner_malicious()
        test_scanner_executable()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
