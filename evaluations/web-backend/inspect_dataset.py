"""
Inspect the Opik dataset structure to understand what data we have for evaluation.
"""
from opik import Opik

# Initialize Opik client
client = Opik()

# Get the dataset
dataset_name = "FretCoach Hub AI Coach Chat"
print(f"📊 Fetching dataset: {dataset_name}\n")

try:
    dataset = client.get_dataset(name=dataset_name)
    print(f"✅ Dataset found: {dataset.name}")

    # Get dataset items
    items = dataset.get_items()
    print(f"📝 Total items in dataset: {len(items)}\n")

    if len(items) > 0:
        print("=" * 80)
        print("DATASET STRUCTURE ANALYSIS")
        print("=" * 80)

        # Analyze first item structure
        first_item = items[0]
        print(f"\n🔍 First Item Keys: {list(first_item.keys())}\n")

        # Print first 3 items with details
        for i, item in enumerate(items[:3], 1):
            print(f"\n{'=' * 80}")
            print(f"ITEM {i}")
            print(f"{'=' * 80}")

            for key, value in item.items():
                if key == 'id':
                    print(f"📌 {key}: {value}")
                elif key == 'input':
                    print(f"💬 {key}: {value}")
                elif key == 'output' or key == 'expected_output':
                    # Truncate long outputs
                    val_str = str(value)
                    if len(val_str) > 200:
                        val_str = val_str[:200] + "..."
                    print(f"🤖 {key}: {val_str}")
                elif key == 'tags':
                    print(f"🏷️  {key}: {value}")
                elif key == 'metadata':
                    print(f"📋 {key}: {value}")
                else:
                    print(f"   {key}: {value}")

        print(f"\n{'=' * 80}")
        print("SUMMARY")
        print(f"{'=' * 80}")
        print(f"Total items: {len(items)}")
        print(f"Available fields: {list(items[0].keys())}")

except Exception as e:
    print(f"❌ Error: {e}")
    print(f"\nMake sure:")
    print(f"  1. OPIK_API_KEY is set in environment")
    print(f"  2. OPIK_WORKSPACE is set in environment")
    print(f"  3. Dataset name '{dataset_name}' exists in Opik")
