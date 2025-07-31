#!/usr/bin/env python3
"""
Test script to validate Lambda functions locally
"""

import sys
import json
from datetime import datetime

# Mock event and context for testing
class MockContext:
    def __init__(self):
        self.function_name = "test-function"
        self.function_version = "$LATEST"
        self.invoked_function_arn = "arn:aws:lambda:ap-south-1:123456789012:function:test-function"
        self.memory_limit_in_mb = "128"
        self.remaining_time_in_millis = lambda: 30000

def test_start_function():
    """Test the start instances function"""
    print("🚀 Testing START instances function...")
    
    try:
        # Import the function
        from start_instances import lambda_handler
        
        # Mock event and context
        event = {}
        context = MockContext()
        
        # Call the function
        result = lambda_handler(event, context)
        
        print("✅ Start function executed successfully!")
        print("📋 Result:")
        print(json.dumps(json.loads(result['body']), indent=2))
        
        return True
        
    except ImportError:
        print("❌ Could not import start_instances module")
        print("💡 Make sure start-instances.py is in the current directory")
        return False
    except Exception as e:
        print(f"❌ Error testing start function: {str(e)}")
        return False

def test_stop_function():
    """Test the stop instances function"""
    print("\n🛑 Testing STOP instances function...")
    
    try:
        # Import the function
        from stop_instances import lambda_handler
        
        # Mock event and context
        event = {}
        context = MockContext()
        
        # Call the function
        result = lambda_handler(event, context)
        
        print("✅ Stop function executed successfully!")
        print("📋 Result:")
        print(json.dumps(json.loads(result['body']), indent=2))
        
        return True
        
    except ImportError:
        print("❌ Could not import stop_instances module")
        print("💡 Make sure stop-instances.py is in the current directory")
        return False
    except Exception as e:
        print(f"❌ Error testing stop function: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Lambda Function Local Test")
    print("=" * 50)
    
    # Test both functions
    start_success = test_start_function()
    stop_success = test_stop_function()
    
    print("\n📊 Test Summary:")
    print(f"Start function: {'✅ PASS' if start_success else '❌ FAIL'}")
    print(f"Stop function:  {'✅ PASS' if stop_success else '❌ FAIL'}")
    
    if start_success and stop_success:
        print("\n🎉 All tests passed! Your Lambda functions are ready for deployment.")
        print("\n💡 Next steps:")
        print("1. Deploy to AWS Lambda via Console")
        print("2. Create EventBridge rules")
        print("3. Test in AWS Console")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        
    sys.exit(0 if (start_success and stop_success) else 1)
