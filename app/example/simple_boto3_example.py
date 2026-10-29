#!/usr/bin/env python3
"""
Simple boto3 example for creating and downloading SSH keys
This is a minimal example showing how to use boto3 directly
"""

import boto3
import os
from datetime import datetime


def create_key_pair_simple(key_name, region='us-east-1'):
    """
    Create an SSH key pair using boto3

    Args:
        key_name (str): Name for the key pair
        region (str): AWS region

    Returns:
        dict: Key pair information including private key
    """
    try:
        # Create EC2 client
        ec2 = boto3.client('ec2', region_name=region)

        # Create key pair
        response = ec2.create_key_pair(KeyName=key_name)

        # Extract information
        key_info = {
            'key_name': response['KeyName'],
            'key_pair_id': response['KeyPairId'],
            'private_key': response['KeyMaterial'],
            'region': region,
            'created_at': datetime.now().isoformat()
        }

        print(f"✅ Key pair '{key_name}' created successfully!")
        print(f"Key Pair ID: {key_info['key_pair_id']}")
        print(f"Region: {region}")

        return key_info

    except Exception as e:
        print(f"❌ Error creating key pair: {e}")
        return None


def save_key_to_file(key_info, filename=None):
    """
    Save SSH key to file with proper permissions

    Args:
        key_info (dict): Key information from create_key_pair_simple
        filename (str): Optional filename, defaults to key_name.pem

    Returns:
        bool: Success status
    """
    if not key_info or not key_info.get('private_key'):
        print("❌ No private key to save")
        return False

    try:
        # Set filename
        if filename is None:
            filename = f"{key_info['key_name']}.pem"

        # Save private key to file
        with open(filename, 'w') as f:
            f.write(key_info['private_key'])

        # Set proper permissions (chmod 400)
        os.chmod(filename, 0o400)

        print(f"💾 SSH key saved to: {filename}")
        print(f"📏 File size: {len(key_info['private_key'])} characters")
        print(f"🔒 Permissions: 400 (read-only for owner)")

        return True

    except Exception as e:
        print(f"❌ Error saving key: {e}")
        return False


def list_key_pairs(region='us-east-1'):
    """
    List all key pairs in the region

    Args:
        region (str): AWS region

    Returns:
        list: List of key pairs
    """
    try:
        # Create EC2 client
        ec2 = boto3.client('ec2', region_name=region)

        # Describe key pairs
        response = ec2.describe_key_pairs()

        key_pairs = []
        for key_pair in response['KeyPairs']:
            key_info = {
                'key_name': key_pair['KeyName'],
                'key_pair_id': key_pair['KeyPairId'],
                'fingerprint': key_pair['KeyFingerprint'],
                'key_type': key_pair.get('KeyType', 'rsa')
            }
            key_pairs.append(key_info)

        print(f"📋 Found {len(key_pairs)} key pairs in {region}")
        for key_pair in key_pairs:
            print(f"  - {key_pair['key_name']} ({key_pair['key_pair_id']})")

        return key_pairs

    except Exception as e:
        print(f"❌ Error listing key pairs: {e}")
        return []


def delete_key_pair(key_name, region='us-east-1'):
    """
    Delete a key pair

    Args:
        key_name (str): Name of the key pair to delete
        region (str): AWS region

    Returns:
        bool: Success status
    """
    try:
        # Create EC2 client
        ec2 = boto3.client('ec2', region_name=region)

        # Delete key pair
        ec2.delete_key_pair(KeyName=key_name)

        print(f"🗑️ Key pair '{key_name}' deleted successfully")
        return True

    except Exception as e:
        print(f"❌ Error deleting key pair: {e}")
        return False


def main():
    """Main function demonstrating boto3 SSH key operations"""
    print("🔑 Simple boto3 SSH Key Example")
    print("=" * 50)

    # Check AWS credentials
    try:
        # Test AWS credentials
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials valid")
        print(f"Account: {identity['Account']}")
        print(f"User: {identity['Arn']}")
    except Exception as e:
        print(f"❌ AWS credentials not found: {e}")
        print("Please set up AWS credentials:")
        print("1. export AWS_ACCESS_KEY_ID='your-key'")
        print("2. export AWS_SECRET_ACCESS_KEY='your-secret'")
        print("3. Or run: aws configure")
        return

    # Example 1: List existing key pairs
    print(f"\n📋 Listing existing key pairs...")
    existing_keys = list_key_pairs('us-east-1')

    # Example 2: Create a new key pair
    print(f"\n🔑 Creating new key pair...")
    key_name = f"boto3-example-{int(datetime.now().timestamp())}"
    key_info = create_key_pair_simple(key_name, 'us-east-1')

    if key_info:
        # Example 3: Save key to file
        print(f"\n💾 Saving key to file...")
        save_success = save_key_to_file(key_info)

        if save_success:
            print(f"\n🎉 SUCCESS! SSH key created and saved!")
            print(f"Key Name: {key_info['key_name']}")
            print(f"File: {key_info['key_name']}.pem")
            print(f"\n🔑 SSH Usage:")
            print(f"ssh -i {key_info['key_name']}.pem ec2-user@<instance-ip>")

            # Example 4: List key pairs again
            print(f"\n📋 Listing key pairs after creation...")
            updated_keys = list_key_pairs('us-east-1')

            # # Example 5: Clean up (optional)
            # print(f"\n🗑️ Cleaning up...")
            # delete_success = delete_key_pair(key_name, 'us-east-1')

            # if delete_success:
            #     print(f"✅ Key pair deleted successfully")
            #     # Remove the local file
            #     try:
            #         os.remove(f"{key_name}.pem")
            #         print(f"✅ Local file removed")
            #     except:
            #         print(f"⚠️ Could not remove local file")
        else:
            print(f"❌ Failed to save key to file")
    else:
        print(f"❌ Failed to create key pair")


def simple_example():
    """Minimal example for quick testing"""
    print("🚀 Quick boto3 SSH Key Example")
    print("=" * 40)

    # Create key pair
    key_name = "quick-test-key"
    key_info = create_key_pair_simple(key_name)

    if key_info:
        # Save to file
        save_key_to_file(key_info)
        print(f"\n✅ Done! Check {key_name}.pem")
    else:
        print(f"❌ Failed to create key pair")


if __name__ == "__main__":
    # Run the full example
    main()

    # Uncomment to run the simple example instead
    # simple_example()
