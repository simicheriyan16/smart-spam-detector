import pandas as pd

print("\n📥 Converting message dataset...\n")

try:
    # Read raw SMS collection file (tab-separated)
    raw_data = pd.read_csv(
        'SMSSpamCollection',
        sep='\t',
        names=['label', 'message'],
        engine='python'
    )
    
    print(f"✅ Raw data loaded: {len(raw_data)} messages")
    print(f"   Labels: {raw_data['label'].value_counts().to_dict()}")
    
    # Save as CSV
    raw_data.to_csv('spam_messages.csv', index=False)
    
    print(f"\n✅ Conversion successful!")
    print(f"   Output: spam_messages.csv")
    print(f"   Total records: {len(raw_data)}")
    
except FileNotFoundError:
    print("❌ Error: 'SMSSpamCollection' file not found.")
    print("\n📥 Download from: https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset")
    print("   Extract SMSSpamCollection file to this directory")
