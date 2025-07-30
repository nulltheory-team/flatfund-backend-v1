#!/usr/bin/env python3
"""
Quick RDS troubleshooting script
"""
import socket
import sys
import time

def test_network_connectivity():
    """Test basic network connectivity to RDS endpoint"""
    host = "flatfund-db.ctqftasebvp9.ap-south-1.rds.amazonaws.com"
    port = 5432
    timeout = 10
    
    print(f"🌐 Testing network connectivity to {host}:{port}")
    print("-" * 60)
    
    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        start_time = time.time()
        result = sock.connect_ex((host, port))
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        if result == 0:
            print(f"✅ Network connection successful!")
            print(f"⏱️  Response time: {response_time:.2f}ms")
            sock.close()
            return True
        else:
            print(f"❌ Network connection failed!")
            print(f"   Error code: {result}")
            print(f"   Time elapsed: {response_time:.2f}ms")
            return False
            
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False
    except socket.timeout:
        print(f"❌ Connection timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        try:
            sock.close()
        except:
            pass

def check_security_recommendations():
    """Provide security group recommendations"""
    print("\n🔒 Security Group Configuration Needed:")
    print("-" * 60)
    print("Your current IP: 103.214.63.45")
    print("")
    print("Required Inbound Rule:")
    print("  Type: PostgreSQL")
    print("  Protocol: TCP") 
    print("  Port: 5432")
    print("  Source: 103.214.63.45/32  (Your IP only)")
    print("")
    print("Alternative (less secure):")
    print("  Source: 0.0.0.0/0  (Allow from anywhere)")

if __name__ == "__main__":
    print("🔍 FlatFund RDS Connectivity Troubleshooter")
    print("=" * 60)
    
    # Test network connectivity first
    network_ok = test_network_connectivity()
    
    if not network_ok:
        check_security_recommendations()
        print("\n💡 Next Steps:")
        print("1. Update your RDS security group with the rule above")
        print("2. Ensure RDS instance is 'Available' (not stopped)")
        print("3. Verify 'Public accessibility' is set to 'Yes'")
        print("4. Run this script again after making changes")
    else:
        print("\n🎉 Network connectivity is working!")
        print("You can now test the full database connection:")
        print("python test_rds_connection.py")
    
    sys.exit(0 if network_ok else 1)
