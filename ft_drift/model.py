# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_model.ipynb.

# %% auto 0
__all__ = ['prep_data', 'model']

# %% ../nbs/03_model.ipynb 2
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score
from .parse import ChatData

# %% ../nbs/03_model.ipynb 3
def prep_data(f1='file_a.jsonl', 
              f2='file_b.jsonl'):
    c1,c2 = ChatData.load_jsonl(f1), ChatData.load_jsonl(f2)
    m1, m2 = c1.to_md(), c2.to_md()
    
    # Create labels
    a_labels = [0] * len(m1)
    b_labels = [1] * len(m2)

    # Combine datasets
    data = m1 + m2
    labels = a_labels + b_labels

    # Create a DataFrame
    df = pd.DataFrame({'text': data, 'label': labels})
    return df

# %% ../nbs/03_model.ipynb 5
def model(df):
    "Fit a model and calculate diagnostics."
    X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=42)
    
    # Create the pipeline
    pat = r"(?u)[\w|<>\-`]+"
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(min_df=.05, 
                                  ngram_range=(1, 3), 
                                  lowercase=False,
                                  token_pattern=pat)
        ),
        ('clf', RandomForestClassifier(random_state=42))
    ])
    
    # Fit the model
    pipeline.fit(X_train, y_train)
    y_pred_prob = pipeline.predict_proba(X_test)[:, 1]

    # Compute ROC AUC score
    pipeline.roc_auc = roc_auc_score(y_test, y_pred_prob)

    # Compute feat impt
    tfidf = pipeline.named_steps['tfidf']
    feature_names = tfidf.get_feature_names_out()
    importances = pipeline.named_steps['clf'].feature_importances_
    indices = np.argsort(importances)[::-1]
    pipeline.top_features = pd.DataFrame({'Feature': [feature_names[i] for i in indices], 
                                          'Importance': importances[indices]})
    return pipeline
