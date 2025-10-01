from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
import pickle
import os
warnings.filterwarnings('ignore')

class NaiveBayesClassifier:
    def __init__(self, model_path='naive_bayes_model.pkl'):
        """Initialize the Naive Bayes classifier"""
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
        self.classifier = MultinomialNB()
        self.model_path = model_path
        self.is_trained = False
        
        # Try to load existing model
        if os.path.exists(model_path):
            self._load_model()
        else:
            print("No pre-trained model found. Training with default data...")
            self._train_with_default_data()
    
    def _get_sample_data(self):
        """Get balanced sample data for training and testing"""
        # Sales/Advertisement texts (label = 1)
        ad_texts = [
            # Direct sales pitches
            "Buy now and get 50% off our premium skincare collection!",
            "Limited time offer: Free shipping on orders over $50",
            "Don't miss out! Flash sale ends tonight - shop now",
            "Upgrade your wardrobe with our new fall collection",
            "Experience luxury with our handcrafted leather goods",
            
            # Product descriptions with sales intent
            "Our revolutionary face cream reduces wrinkles in just 7 days",
            "This smartwatch tracks your fitness goals and monitors heart rate",
            "Premium coffee beans sourced directly from Colombian farms",
            "Wireless headphones with noise cancellation technology",
            "Eco-friendly cleaning products that are safe for your family",
            
            # Promotional content
            "Subscribe today and get your first month free",
            "Join thousands of satisfied customers who love our service",
            "Try our meal kit delivery service - fresh ingredients delivered daily",
            "Sign up for our premium membership and save 30%",
            "Download our app and get exclusive deals",
            
            # Call-to-action focused
            "Order now and receive a complimentary gift with purchase",
            "Visit our store this weekend for amazing deals",
            "Call now to speak with our product specialists",
            "Click here to start your free trial today",
            "Reserve your spot - limited availability",
            
            # Product launches
            "Introducing our newest smartphone with advanced AI features",
            "Pre-order the latest gaming console - ships December 15th",
            "New arrival: Designer handbags at unbeatable prices",
            "Launch special: 40% off our new fitness equipment line",
            "Be the first to try our innovative home security system"
        ]
        
        # Non-advertisement texts (label = 0)
        non_ad_texts = [
            # News and information
            "The weather forecast shows rain expected throughout the week",
            "Local government announces new infrastructure development plans",
            "Scientists discover new species in the Amazon rainforest",
            "Stock market shows mixed results in today's trading session",
            "New study reveals benefits of Mediterranean diet",
            
            # Educational content
            "Machine learning algorithms can be classified into supervised and unsupervised",
            "The Renaissance period marked a significant cultural shift in Europe",
            "Photosynthesis is the process by which plants convert sunlight into energy",
            "Climate change affects global weather patterns significantly",
            "Programming languages have different paradigms and use cases",
            
            # Social media posts (non-commercial)
            "Had a great time at the concert last night with friends",
            "Beautiful sunset from my hike this morning",
            "Excited to start my new job next week",
            "Thanks everyone for the birthday wishes",
            "Looking forward to the weekend camping trip",
            
            # Questions and discussions
            "What's the best way to learn a new programming language?",
            "Has anyone tried the new restaurant downtown?",
            "How do you manage work-life balance effectively?",
            "Which book would you recommend for personal development?",
            "What are your thoughts on renewable energy adoption?",
            
            # Informational content
            "The library will be closed for maintenance this Thursday",
            "Traffic on Highway 101 is delayed due to construction",
            "University announces new scholarship programs for students",
            "Local farmer's market operates every Saturday morning",
            "Community center offers free computer classes for seniors"
        ]
        
        all_texts = ad_texts + non_ad_texts
        all_labels = [1] * len(ad_texts) + [0] * len(non_ad_texts)
        
        return all_texts, all_labels
    
    def _train_with_default_data(self):
        """Train and test the classifier with default data"""
        texts, labels = self._get_sample_data()
        
        # Split data (70% train, 30% test)
        train_texts, test_texts, train_labels, test_labels = train_test_split(
            texts, labels, test_size=0.3, random_state=42, stratify=labels
        )
        
        print(f"Total samples: {len(texts)} (Ads: {sum(labels)}, Non-ads: {len(labels) - sum(labels)})")
        print(f"Training samples: {len(train_texts)}")
        print(f"Testing samples: {len(test_texts)}")
        
        # Train
        print("\nTraining Naive Bayes classifier...")
        X_train = self.vectorizer.fit_transform(train_texts)
        self.classifier.fit(X_train, train_labels)
        self.is_trained = True
        
        # Test
        X_test = self.vectorizer.transform(test_texts)
        predictions = self.classifier.predict(X_test)
        accuracy = accuracy_score(test_labels, predictions)
        
        print(f"\nTraining complete!")
        print(f"Test Accuracy: {accuracy:.4f}")
        print(f"\nClassification Report:")
        print(classification_report(test_labels, predictions, target_names=['Not Ad', 'Ad']))
        
        # Save model
        self._save_model()
    
    def predict(self, text):
        """
        Predict if the text is an ad or not.
        
        Args:
            text (str): Input text to classify
            
        Returns:
            int: 1 if ad, 0 if not ad
        """
        if not self.is_trained:
            print("Warning: Model not trained yet!")
            return 0
        
        if not text or not isinstance(text, str):
            return 0
        
        X_test = self.vectorizer.transform([text])
        prediction = self.classifier.predict(X_test)[0]
        return int(prediction)
    
    def predict_batch(self, texts):
        """
        Predict multiple texts at once.
        
        Args:
            texts (list): List of input texts to classify
            
        Returns:
            list: List of predictions (1 for ad, 0 for not ad)
        """
        if not self.is_trained:
            print("Warning: Model not trained yet!")
            return [0] * len(texts)
        
        if not texts:
            return []
        
        X_test = self.vectorizer.transform(texts)
        predictions = self.classifier.predict(X_test)
        return predictions.tolist()
    
    def _save_model(self):
        """Save the trained model and vectorizer"""
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'classifier': self.classifier,
                'is_trained': self.is_trained
            }, f)
        print(f"Model saved to {self.model_path}")
    
    def _load_model(self):
        """Load a pre-trained model"""
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.vectorizer = data['vectorizer']
                self.classifier = data['classifier']
                self.is_trained = data['is_trained']
            print(f"Model loaded from {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self._train_with_default_data()


# Test the classifier when running this file directly
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing NaiveBayesClassifier")
    print("="*60 + "\n")
    
    # Initialize classifier (this will train if no model exists)
    clf = NaiveBayesClassifier()
    
    # Test texts
    print("\n" + "="*60)
    print("Testing predictions on sample texts")
    print("="*60 + "\n")
    
    test_texts = [
        "Buy now! Limited offer!",
        "Get 50% off today only - shop now!",
        "The weather is nice today.",
        "I'm having dinner with my family tonight.",
        "Subscribe and save 30% on your first order!",
        "The meeting is scheduled for 3 PM tomorrow.",
        "Limited time: Free shipping on all orders!",
        "I just finished reading a great book."
    ]
    
    for text in test_texts:
        result = clf.predict(text)
        label = "AD" if result == 1 else "NOT AD"
        print(f"[{label}] {text}")
    
    print(f"\n{'='*60}")
    print("Testing on additional sales texts")
    print("="*60 + "\n")
    
    sales_texts = [
        "Upgrade your mornings with our premium coffee blend — rich, bold, unforgettable.",
        "Don't miss out! Grab our limited-edition sneakers before they sell out.",
        "Transform your skin with our dermatologist-approved serum — shop now.",
        "Save 30% this weekend only on all home décor items.",
        "Sign up today and get your first month of fitness classes free.",
        "Turn every shower into a spa with our aromatherapy shower bombs.",
        "Experience the crisp sound of our wireless earbuds — now with noise cancellation.",
    ]
    
    for text in sales_texts:
        result = clf.predict(text)
        label = "AD" if result == 1 else "NOT AD"
        print(f"[{label}] {text}")
