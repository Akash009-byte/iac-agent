"""
EC2 Pricing Tools for cost analysis
"""

import requests
import json
from typing import Dict, Any, Optional
from strands import tool


@tool
def get_ec2_pricing(instance_type: str, region: str = "us-east-1") -> str:
    """
    Get EC2 instance pricing information for cost analysis.

    Args:
        instance_type: EC2 instance type (e.g., t2.micro, t3.medium, m5.large)
        region: AWS region (default: us-east-1)

    Returns:
        String with detailed pricing information and cost analysis
    """
    try:
        # EC2 pricing data (approximate rates as of 2024)
        # These are rough estimates - actual pricing may vary
        pricing_data = {
            "us-east-1": {
                "t2.micro": {"hourly": 0.0116, "description": "1 vCPU, 1 GB RAM"},
                "t2.small": {"hourly": 0.023, "description": "1 vCPU, 2 GB RAM"},
                "t2.medium": {"hourly": 0.0464, "description": "2 vCPU, 4 GB RAM"},
                "t2.large": {"hourly": 0.0928, "description": "2 vCPU, 8 GB RAM"},
                "t2.xlarge": {"hourly": 0.1856, "description": "4 vCPU, 16 GB RAM"},
                "t2.2xlarge": {"hourly": 0.3712, "description": "8 vCPU, 32 GB RAM"},
                "t3.micro": {"hourly": 0.0104, "description": "2 vCPU, 1 GB RAM"},
                "t3.small": {"hourly": 0.0208, "description": "2 vCPU, 2 GB RAM"},
                "t3.medium": {"hourly": 0.0416, "description": "2 vCPU, 4 GB RAM"},
                "t3.large": {"hourly": 0.0832, "description": "2 vCPU, 8 GB RAM"},
                "t3.xlarge": {"hourly": 0.1664, "description": "4 vCPU, 16 GB RAM"},
                "t3.2xlarge": {"hourly": 0.3328, "description": "8 vCPU, 32 GB RAM"},
                "m5.large": {"hourly": 0.096, "description": "2 vCPU, 8 GB RAM"},
                "m5.xlarge": {"hourly": 0.192, "description": "4 vCPU, 16 GB RAM"},
                "m5.2xlarge": {"hourly": 0.384, "description": "8 vCPU, 32 GB RAM"},
                "m5.4xlarge": {"hourly": 0.768, "description": "16 vCPU, 64 GB RAM"},
                "c5.large": {"hourly": 0.085, "description": "2 vCPU, 4 GB RAM"},
                "c5.xlarge": {"hourly": 0.17, "description": "4 vCPU, 8 GB RAM"},
                "c5.2xlarge": {"hourly": 0.34, "description": "8 vCPU, 16 GB RAM"},
                "r5.large": {"hourly": 0.126, "description": "2 vCPU, 16 GB RAM"},
                "r5.xlarge": {"hourly": 0.252, "description": "4 vCPU, 32 GB RAM"},
            },
            "us-west-1": {
                "t2.micro": {"hourly": 0.0139, "description": "1 vCPU, 1 GB RAM"},
                "t2.small": {"hourly": 0.0278, "description": "1 vCPU, 2 GB RAM"},
                "t2.medium": {"hourly": 0.0556, "description": "2 vCPU, 4 GB RAM"},
                "t2.large": {"hourly": 0.1112, "description": "2 vCPU, 8 GB RAM"},
                "t2.xlarge": {"hourly": 0.2224, "description": "4 vCPU, 16 GB RAM"},
                "t2.2xlarge": {"hourly": 0.4448, "description": "8 vCPU, 32 GB RAM"},
                "t3.micro": {"hourly": 0.0125, "description": "2 vCPU, 1 GB RAM"},
                "t3.small": {"hourly": 0.025, "description": "2 vCPU, 2 GB RAM"},
                "t3.medium": {"hourly": 0.05, "description": "2 vCPU, 4 GB RAM"},
                "t3.large": {"hourly": 0.1, "description": "2 vCPU, 8 GB RAM"},
                "t3.xlarge": {"hourly": 0.2, "description": "4 vCPU, 16 GB RAM"},
                "t3.2xlarge": {"hourly": 0.4, "description": "8 vCPU, 32 GB RAM"},
                "m5.large": {"hourly": 0.115, "description": "2 vCPU, 8 GB RAM"},
                "m5.xlarge": {"hourly": 0.23, "description": "4 vCPU, 16 GB RAM"},
                "m5.2xlarge": {"hourly": 0.46, "description": "8 vCPU, 32 GB RAM"},
                "m5.4xlarge": {"hourly": 0.92, "description": "16 vCPU, 64 GB RAM"},
                "c5.large": {"hourly": 0.102, "description": "2 vCPU, 4 GB RAM"},
                "c5.xlarge": {"hourly": 0.204, "description": "4 vCPU, 8 GB RAM"},
                "c5.2xlarge": {"hourly": 0.408, "description": "8 vCPU, 16 GB RAM"},
                "r5.large": {"hourly": 0.151, "description": "2 vCPU, 16 GB RAM"},
                "r5.xlarge": {"hourly": 0.302, "description": "4 vCPU, 32 GB RAM"},
            },
            "us-east-2": {
                "t2.micro": {"hourly": 0.0116, "description": "1 vCPU, 1 GB RAM"},
                "t2.small": {"hourly": 0.023, "description": "1 vCPU, 2 GB RAM"},
                "t2.medium": {"hourly": 0.0464, "description": "2 vCPU, 4 GB RAM"},
                "t2.large": {"hourly": 0.0928, "description": "2 vCPU, 8 GB RAM"},
                "t2.xlarge": {"hourly": 0.1856, "description": "4 vCPU, 16 GB RAM"},
                "t2.2xlarge": {"hourly": 0.3712, "description": "8 vCPU, 32 GB RAM"},
                "t3.micro": {"hourly": 0.0104, "description": "2 vCPU, 1 GB RAM"},
                "t3.small": {"hourly": 0.0208, "description": "2 vCPU, 2 GB RAM"},
                "t3.medium": {"hourly": 0.0416, "description": "2 vCPU, 4 GB RAM"},
                "t3.large": {"hourly": 0.0832, "description": "2 vCPU, 8 GB RAM"},
                "t3.xlarge": {"hourly": 0.1664, "description": "4 vCPU, 16 GB RAM"},
                "t3.2xlarge": {"hourly": 0.3328, "description": "8 vCPU, 32 GB RAM"},
                "m5.large": {"hourly": 0.096, "description": "2 vCPU, 8 GB RAM"},
                "m5.xlarge": {"hourly": 0.192, "description": "4 vCPU, 16 GB RAM"},
                "m5.2xlarge": {"hourly": 0.384, "description": "8 vCPU, 32 GB RAM"},
                "m5.4xlarge": {"hourly": 0.768, "description": "16 vCPU, 64 GB RAM"},
                "c5.large": {"hourly": 0.085, "description": "2 vCPU, 4 GB RAM"},
                "c5.xlarge": {"hourly": 0.17, "description": "4 vCPU, 8 GB RAM"},
                "c5.2xlarge": {"hourly": 0.34, "description": "8 vCPU, 16 GB RAM"},
                "r5.large": {"hourly": 0.126, "description": "2 vCPU, 16 GB RAM"},
                "r5.xlarge": {"hourly": 0.252, "description": "4 vCPU, 32 GB RAM"},
            }
        }

        # Get pricing for the specified region and instance type
        if region not in pricing_data:
            return f"❌ Region '{region}' not supported. Supported regions: us-east-1, us-west-1, us-east-2"

        if instance_type not in pricing_data[region]:
            available_types = ", ".join(pricing_data[region].keys())
            return f"❌ Instance type '{instance_type}' not found in {region}. Available types: {available_types}"

        pricing = pricing_data[region][instance_type]
        hourly_rate = pricing["hourly"]
        description = pricing["description"]

        # Calculate cost estimates
        daily_cost = hourly_rate * 24
        monthly_cost = daily_cost * 30
        yearly_cost = monthly_cost * 12

        # Format the response
        cost_analysis = f"""
💰 **EC2 Instance Cost Analysis**

**Instance Details:**
- **Type**: {instance_type}
- **Region**: {region}
- **Specifications**: {description}

**Pricing Breakdown:**
- **Hourly Rate**: ${hourly_rate:.4f}/hour
- **Daily Cost**: ${daily_cost:.2f}/day
- **Monthly Cost**: ${monthly_cost:.2f}/month (30 days)
- **Yearly Cost**: ${yearly_cost:.2f}/year

**Cost Scenarios:**
- **Light Usage** (8 hours/day): ${hourly_rate * 8:.2f}/day
- **Business Hours** (12 hours/day): ${hourly_rate * 12:.2f}/day
- **Always On** (24/7): ${daily_cost:.2f}/day

**Important Notes:**
- ⚠️ These are **estimated costs** based on current AWS pricing
- 💡 Actual costs may vary based on usage patterns and data transfer
- 🔄 Prices can change without notice
- 📊 Consider using Reserved Instances for long-term cost savings
- 🎯 Free tier eligible instances (t2.micro) have usage limits

**Regional Comparison:**
"""

        # Add regional comparison
        for reg, data in pricing_data.items():
            if instance_type in data:
                reg_hourly = data[instance_type]["hourly"]
                cost_analysis += f"- **{reg}**: ${reg_hourly:.4f}/hour\n"

        cost_analysis += f"""
**Recommendation:**
This instance type is suitable for {'development/testing' if 'micro' in instance_type or 'small' in instance_type else 'production workloads'}.

Do you want to proceed with creating this instance? Please confirm with 'yes' or 'proceed'.
"""

        return cost_analysis

    except Exception as e:
        return f"❌ Error fetching pricing information: {str(e)}"


@tool
def compare_ec2_pricing(instance_types: str, region: str = "us-east-1") -> str:
    """
    Compare pricing between multiple EC2 instance types.

    Args:
        instance_types: Comma-separated list of instance types (e.g., "t2.micro,t3.micro,m5.large")
        region: AWS region (default: us-east-1)

    Returns:
        String with pricing comparison table
    """
    try:
        types_list = [t.strip() for t in instance_types.split(",")]

        comparison = f"""
📊 **EC2 Instance Pricing Comparison - {region}**

| Instance Type | Hourly Rate | Daily Cost | Monthly Cost | Description |
|---------------|-------------|------------|--------------|-------------|
"""

        # Use the same pricing data from get_ec2_pricing
        pricing_data = {
            "us-east-1": {
                "t2.micro": {"hourly": 0.0116, "description": "1 vCPU, 1 GB RAM"},
                "t2.small": {"hourly": 0.023, "description": "1 vCPU, 2 GB RAM"},
                "t2.medium": {"hourly": 0.0464, "description": "2 vCPU, 4 GB RAM"},
                "t2.large": {"hourly": 0.0928, "description": "2 vCPU, 8 GB RAM"},
                "t3.micro": {"hourly": 0.0104, "description": "2 vCPU, 1 GB RAM"},
                "t3.small": {"hourly": 0.0208, "description": "2 vCPU, 2 GB RAM"},
                "t3.medium": {"hourly": 0.0416, "description": "2 vCPU, 4 GB RAM"},
                "t3.large": {"hourly": 0.0832, "description": "2 vCPU, 8 GB RAM"},
                "m5.large": {"hourly": 0.096, "description": "2 vCPU, 8 GB RAM"},
                "m5.xlarge": {"hourly": 0.192, "description": "4 vCPU, 16 GB RAM"},
            }
        }

        if region not in pricing_data:
            return f"❌ Region '{region}' not supported for comparison."

        for instance_type in types_list:
            if instance_type in pricing_data[region]:
                pricing = pricing_data[region][instance_type]
                hourly = pricing["hourly"]
                daily = hourly * 24
                monthly = daily * 30
                description = pricing["description"]

                comparison += f"| {instance_type} | ${hourly:.4f} | ${daily:.2f} | ${monthly:.2f} | {description} |\n"
            else:
                comparison += f"| {instance_type} | N/A | N/A | N/A | Not available |\n"

        comparison += f"""
**Summary:**
- Most cost-effective: {min(types_list, key=lambda x: pricing_data[region].get(x, {}).get('hourly', float('inf')))}
- Best performance: {max(types_list, key=lambda x: pricing_data[region].get(x, {}).get('hourly', 0))}

Choose the instance type that best fits your needs and budget.
"""

        return comparison

    except Exception as e:
        return f"❌ Error comparing pricing: {str(e)}"
