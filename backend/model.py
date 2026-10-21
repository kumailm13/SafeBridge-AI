import os
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def generate_synthetic_data() -> pd.DataFrame:
    safe_data = [
        "How do I cook a steak in a cast iron skillet?",
        "What is the weather forecast for Islamabad this weekend?",
        "Write a Python script to sort a list of numbers using quicksort.",
        "Tell me a joke about computer science and robotics.",
        "Explain quantum entanglement in simple terms for a high school student.",
        "How can our marketing team improve organic search ranking?",
        "What are the cardiovascular benefits of regular aerobic exercise?",
        "How to build a responsive web interface using React and Tailwind CSS?",
        "What are the best tourist destinations to visit in northern Pakistan?",
        "How does a four-stroke internal combustion engine cycle work?",
        "Can you write a polite email asking for an update on our project deadline?",
        "Translate this welcome message from English to Urdu.",
        "What is the difference between TCP and UDP protocols?",
        "Summarize the main themes of Shakespeare's Macbeth.",
        "How do convolutional neural networks process image feature maps?",
        "Give me 5 creative ideas for a team building retreat.",
        "Write a SQL query to join customer orders with product inventory.",
        "What are the best practices for clean architecture in software development?",
        "Explain the difference between supervised and unsupervised learning algorithms.",
        "Help me format this markdown table for our open-source documentation.",
        "How to implement binary search in C++?",
        "What is the history of COMSATS University Islamabad?",
        "Provide a summary of the Paris Climate Agreement.",
        "How do I configure nginx as a reverse proxy for a web application?",
        "What are some healthy lunch ideas for office workers?",
        "Explain how public key cryptography and RSA signatures work in theory.",
        "Write a sample unit test using pytest for a calculator function.",
        "Can you help proofread this cover letter for a software internship?",
        "How does DNS resolution translate domain names to IP addresses?",
        "What is the role of mitochondria in human cellular metabolism?"
    ]

    sensitive_data = [
        "My root server password is admin_secret_pass_1234",
        "The company secret project code is Project_Zeus_TopSecret_99",
        "My national CNIC number is 37405-1234567-3, do not disclose it",
        "Here is our production database connection string: postgresql://admin:SuperSecret2026@db.internal:5432/corp_prod",
        "Confidential memo: Do not share this internal financial projection with external auditors.",
        "The Q4 unannounced revenue balance is strictly confidential and under NDA.",
        "Employee executive salary list: CEO: 1.5M PKR, CTO: 1.2M PKR, Lead Dev: 800k PKR.",
        "My private personal email address is confidential_ceo@corporate.internal.pk",
        "Customer Mastercard number 5425 2334 8901 2345 expiring 12/28 with CVV 412",
        "The complete hardware architectural blueprint for our new patent is attached in this folder.",
        "Here is the AWS secret access key: AKIAIOSFODNN7EXAMPLE and secret: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "Strictly private internal audit findings: Critical SQL injection vulnerability discovered on auth service.",
        "Confidential merger discussion between our firm and competitor X.",
        "Client credit card records: Visa 4111 2222 3333 4444, exp 09/27, CVV 891.",
        "Employee CNIC data sheet: Ali 61101-9876543-1, Sara 37201-1122334-2.",
        "Exported user passwords hash file from production database table.",
        "Do not leak this document: Proprietary machine learning model training parameters and weights.",
        "Internal HR disciplinary investigation regarding employee conduct.",
        "Restricted access credentials for the staging Kubernetes cluster: bearer token eyJhbGciOi...",
        "The secret API key for our billing gateway is sk-live-9921820491823901.",
        "Confidential customer contact directory containing personal cell phone numbers and home addresses.",
        "Restricted trade secrets regarding our proprietary chemical formulation.",
        "Internal vulnerability report: Unpatched zero-day exploit in our payment gateway.",
        "Confidential shareholder equity distribution and cap table.",
        "Here are the private SSH keys for our production jump server: -----BEGIN RSA PRIVATE KEY-----"
    ]

    df = pd.DataFrame({
        "text": safe_data + sensitive_data,
        "label": [0] * len(safe_data) + [1] * len(sensitive_data)
    })
    return df

def train_model():
    print("[Trainer] Generating synthetic dataset for sensitivity classification...")
    df = generate_synthetic_data()
    print(f"[Trainer] Total samples: {len(df)} (Safe: {sum(df['label'] == 0)}, Sensitive: {sum(df['label'] == 1)})")

    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['label'], test_size=0.25, random_state=42, stratify=df['label']
    )

    print("[Trainer] Vectorizing text with TF-IDF...")
    vectorizer = TfidfVectorizer(max_features=1500, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("[Trainer] Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_vec, y_train)

    # Evaluate
    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"[Trainer] Test Accuracy: {acc * 100:.2f}%")
    print("\n[Trainer] Classification Report:\n", classification_report(y_test, y_pred))

    # Save artifacts to models directory
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(cur_dir)
    target_models_dir = os.path.join(repo_root, "models")
    os.makedirs(target_models_dir, exist_ok=True)

    model_path = os.path.join(target_models_dir, "sensitivity_model.pkl")
    vectorizer_path = os.path.join(target_models_dir, "vectorizer.pkl")

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    print(f"[Trainer] Model successfully saved to {model_path}")
    print(f"[Trainer] Vectorizer successfully saved to {vectorizer_path}")

def load_model():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(cur_dir)
    model_path = os.path.join(repo_root, "models", "sensitivity_model.pkl")
    vectorizer_path = os.path.join(repo_root, "models", "vectorizer.pkl")
    if os.path.exists(model_path) and os.path.exists(vectorizer_path):
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        return model, vectorizer
    return None, None

if __name__ == "__main__":
    train_model()
