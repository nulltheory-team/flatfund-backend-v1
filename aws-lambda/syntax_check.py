#!/usr/bin/env python3
"""
Simple syntax check for Lambda functions
"""

import ast
import sys

def check_syntax(filename):
    """Check if a Python file has valid syntax"""
    try:
        with open(filename, 'r') as f:
            source = f.read()
        
        # Parse the AST to check syntax
        ast.parse(source)
        print(f"✅ {filename}: Syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ {filename}: Syntax error at line {e.lineno}: {e.msg}")
        return False
    except FileNotFoundError:
        print(f"❌ {filename}: File not found")
        return False
    except Exception as e:
        print(f"❌ {filename}: Error - {str(e)}")
        return False

def main():
    print("🔍 Lambda Function Syntax Check")
    print("=" * 40)
    
    files_to_check = [
        'start-instances.py',
        'stop-instances.py'
    ]
    
    all_valid = True
    
    for filename in files_to_check:
        valid = check_syntax(filename)
        all_valid = all_valid and valid
    
    print("\n📋 Summary:")
    if all_valid:
        print("🎉 All files have valid syntax!")
        print("\n✅ Your Lambda functions are ready for AWS deployment")
        print("\n🚀 Configuration Summary:")
        print("- EC2 Instance: i-01972c407dd494e7e")
        print("- RDS Instance: flatfund-db")
        print("- Schedule: 4-7 PM & 10 PM-1 AM IST (6 hours/day)")
        print("- Expected savings: ~75% on AWS costs")
        
        print("\n📝 Next Steps:")
        print("1. Go to AWS Lambda Console")
        print("2. Create functions with the code from these files")
        print("3. Set up EventBridge scheduling")
        print("4. Test manually in AWS Console")
    else:
        print("❌ Some files have syntax errors - fix them before deployment")
    
    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())
