"""
Test script for the FastAPI Text-to-Speech backend
Run this to verify everything is working correctly
"""

import requests
import json
import base64
import sys

API_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("\n🔍 Testing health check...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed:", response.json())
            return True
        else:
            print("❌ Health check failed:", response.status_code)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure the FastAPI server is running: python main.py")
        return False


def test_synthesize():
    """Test the synthesize endpoint"""
    print("\n🔍 Testing text synthesis...")
    
    request_body = {
        "text": "Hello, this is a test of the text-to-speech system.",
        "prompt": "Read aloud in a friendly and clear tone",
        "voice_name": "Achernar",
        "language_code": "en-US",
        "model_name": "gemini-2.5-pro-tts",
        "audio_encoding": "LINEAR16",
        "pitch": 0.0,
        "speaking_rate": 1.0
    }

    try:
        response = requests.post(
            f"{API_URL}/synthesize",
            json=request_body,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Synthesis successful!")
                print(f"   Message: {result.get('message')}")
                print(f"   Audio duration: {result.get('audio_duration')} seconds")
                print(f"   Audio content length: {len(result.get('audio_content', ''))} chars")
                return True
            else:
                print("❌ Synthesis failed:", result.get("message"))
                return False
        else:
            print(f"❌ API error {response.status_code}:")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Cannot reach API server")
        print("   Make sure the FastAPI server is running: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_stream():
    """Test the stream endpoint"""
    print("\n🔍 Testing audio stream...")
    
    request_body = {
        "text": "Welcome to the streaming audio test.",
        "prompt": "Read aloud naturally",
        "voice_name": "Achernar"
    }

    try:
        response = requests.post(
            f"{API_URL}/synthesize/stream",
            json=request_body,
            timeout=30
        )
        
        if response.status_code == 200:
            audio_data = response.content
            print(f"✅ Stream successful!")
            print(f"   Audio data size: {len(audio_data)} bytes")
            return True
        else:
            print(f"❌ Stream failed {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_with_different_voices():
    """Test with different voice options"""
    print("\n🔍 Testing different voices...")
    
    voices = ["Achernar", "Altair", "Vega"]
    test_text = "Hello, testing voice variations."
    
    for voice in voices:
        request_body = {
            "text": test_text,
            "voice_name": voice,
            "prompt": f"Use the {voice} voice"
        }
        
        try:
            response = requests.post(
                f"{API_URL}/synthesize",
                json=request_body,
                timeout=30
            )
            
            if response.status_code == 200 and response.json().get("success"):
                print(f"   ✅ {voice}: OK")
            else:
                print(f"   ❌ {voice}: Failed")
        except Exception as e:
            print(f"   ❌ {voice}: Error - {e}")


def test_error_handling():
    """Test error handling"""
    print("\n🔍 Testing error handling...")
    
    # Test empty text
    print("   Testing empty text...")
    response = requests.post(
        f"{API_URL}/synthesize",
        json={"text": ""},
        timeout=5
    )
    if response.status_code == 400:
        print("   ✅ Empty text validation works")
    else:
        print("   ❌ Empty text validation failed")
    
    # Test very long text
    print("   Testing text length limit...")
    long_text = "a" * 10000
    response = requests.post(
        f"{API_URL}/synthesize",
        json={"text": long_text},
        timeout=5
    )
    if response.status_code == 400:
        print("   ✅ Text length limit works")
    else:
        print("   ❌ Text length limit failed")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("FastAPI Text-to-Speech Backend - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test health
    results.append(("Health Check", test_health_check()))
    
    if results[0][1]:  # Only continue if health check passed
        results.append(("Synthesize", test_synthesize()))
        results.append(("Stream", test_stream()))
        test_with_different_voices()
        test_error_handling()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
