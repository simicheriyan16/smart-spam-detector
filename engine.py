import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pickle
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*70)
print("📧 SPAM DETECTION ENGINE - TRAINING MODULE")
print("="*70 + "\n")

print("🔄 Loading SMS dataset...")
try:
    dataset = pd.read_csv("spam_messages.csv")
    print(f"✅ Dataset loaded: {len(dataset)} messages")
    print(f"   Columns: {list(dataset.columns)}")
except FileNotFoundError:
    print("❌ Error: 'spam_messages.csv' not found.")
    print("   Please download from Kaggle or use convert_messages.py")
    exit()

print(f"\n📊 Dataset Statistics:")
print(dataset['label'].value_counts())

# Data preparation
message_features = dataset['message']
message_labels = dataset['label']

print(f"\n🔀 Splitting dataset (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(
    message_features,
    message_labels,
    test_size=0.2,
    random_state=42,
    stratify=message_labels
)

print(f"   Training: {len(X_train)} messages")
print(f"   Testing: {len(X_test)} messages")

print(f"\n🔤 Extracting TF-IDF features...")
feature_extractor = TfidfVectorizer(
    max_features=3000,
    stop_words='english',
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.8,
    sublinear_tf=True
)

X_train_transformed = feature_extractor.fit_transform(X_train)
X_test_transformed = feature_extractor.transform(X_test)

print(f"✅ Feature extraction complete")
print(f"   Feature space: {X_train_transformed.shape}")

print(f"\n🧠 Training SVM classifier...")
classifier = LinearSVC(
    C=1.0,
    max_iter=2000,
    random_state=42,
    dual='auto'
)

classifier.fit(X_train_transformed, y_train)
print("✅ Model training complete")

print(f"\n🧪 Evaluating performance...")
predictions = classifier.predict(X_test_transformed)

acc = accuracy_score(y_test, predictions)
prec = precision_score(y_test, predictions, zero_division=0)
rec = recall_score(y_test, predictions, zero_division=0)
f1 = f1_score(y_test, predictions, zero_division=0)

print(f"   Accuracy:  {acc*100:.2f}%")
print(f"   Precision: {prec*100:.2f}%")
print(f"   Recall:    {rec*100:.2f}%")
print(f"   F1-Score:  {f1*100:.2f}%")

print(f"\n💾 Saving model artifacts...")
pickle.dump(classifier, open('spam_classifier.pkl', 'wb'))
pickle.dump(feature_extractor, open('tfidf_extractor.pkl', 'wb'))

print(f"   ✓ spam_classifier.pkl")
print(f"   ✓ tfidf_extractor.pkl")

print("\n" + "="*70)
print("✅ Training complete! Ready for deployment.")
print("   Run: python service.py")
print("="*70 + "\n")
