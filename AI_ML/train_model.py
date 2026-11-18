import pandas as pd
import numpy as np
import os, joblib, matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (classification_report, accuracy_score,
                             mean_squared_error, confusion_matrix)

df = pd.read_csv("./data/processed/synthetic_dataset.csv")

X = df[['rooftop_area_m2','open_area_m2','roof_type',
        'num_persons','per_capita','period_days',
        'rainfall_mm','soil_type','lithology_type','depth_mbgl']]

y = df['recommended_action']

categorical = ['roof_type','soil_type','lithology_type']
numeric = [col for col in X.columns if col not in categorical]

preprocess = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical),
    ('num', StandardScaler(), numeric)
])

clf_model = RandomForestClassifier(n_estimators=300, class_weight='balanced_subsample', random_state=42, n_jobs=-1)
clf = Pipeline([('preprocess', preprocess), ('model', clf_model)])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, test_size=0.2, random_state=42
)

clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

print("Classification Report:")
print(classification_report(y_test, y_pred))
acc = accuracy_score(y_test, y_pred)
print(f"Classifier Accuracy: {acc:.4f}")

os.makedirs("models", exist_ok=True)
os.makedirs("plots", exist_ok=True)

cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt="d", xticklabels=clf.classes_, yticklabels=clf.classes_, cmap="Blues")
plt.title("Confusion Matrix - Structure Classification")
plt.ylabel("True Label")
plt.xlabel("Predicted Label")
plt.tight_layout()
plt.savefig("plots/confusion_matrix_classification.png", dpi=300)
plt.close()

ohe = clf.named_steps['preprocess'].named_transformers_['cat']
feature_names_cat = list(ohe.get_feature_names_out(categorical))
feature_names = feature_names_cat + numeric

importances = clf.named_steps['model'].feature_importances_
feat_imp = pd.Series(importances, index=feature_names).sort_values(ascending=False)

plt.figure(figsize=(10,6))
sns.barplot(x=feat_imp[:15], y=feat_imp.index[:15], palette="viridis", legend=False)
plt.title("Top 15 Feature Importances - Structure Classifier")
plt.xlabel("Importance")
plt.tight_layout()
plt.savefig("plots/classifier_feature_importance.png", dpi=300)
plt.close()

joblib.dump(clf, "models/structure_classifier.pkl")

dimension_models = {}
dimension_map = {
    'store_on_roof': ['tank_height_m','tank_diameter_m','tank_volume_l'],
    'recharge_well_or_injection': ['well_depth_m','well_diameter_m','injection_capacity_lps'],
    'recharge_on_site_pit': ['pit_depth_m','pit_diameter_m'],
    'recharge_shaft': ['shaft_depth_m','shaft_diameter_m'],
    'community_recharge_or_combination': ['comm_structure_depth_m','comm_structure_diameter_m'],
    'recharge_shaft_or_community': ['comm_structure_depth_m','comm_structure_diameter_m']
}

for structure_type, dim_cols in dimension_map.items():
    if structure_type == 'community_recharge_or_combination':
        subset = df[df['recommended_action'].isin([structure_type, 'recharge_shaft_or_community'])].copy()
    else:
        subset = df[df['recommended_action']==structure_type].copy()
    if subset.empty:
        continue

    X_sub = subset[X.columns]
    y_sub = subset[dim_cols]

    reg_model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    reg_pipeline = Pipeline([('preprocess', preprocess), ('model', reg_model)])

    X_train, X_test, y_train, y_test = train_test_split(
        X_sub, y_sub, test_size=0.2, random_state=42
    )

    reg_pipeline.fit(X_train, y_train)
    y_pred = reg_pipeline.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    print(f"\nRegression performance for {structure_type}:")
    print("MSE:", mse)

    for i, col in enumerate(dim_cols):
        plt.figure(figsize=(5,5))
        plt.scatter(y_test.iloc[:,i], y_pred[:,i], alpha=0.6)
        plt.plot([y_test.iloc[:,i].min(), y_test.iloc[:,i].max()],
                 [y_test.iloc[:,i].min(), y_test.iloc[:,i].max()], 'r--')
        plt.xlabel("Actual")
        plt.ylabel("Predicted")
        plt.title(f"Predicted vs Actual - {structure_type} ({col})")
        plt.tight_layout()
        plt.savefig(f"plots/{structure_type}_{col}_scatter.png", dpi=300)
        plt.close()

    importances = reg_pipeline.named_steps['model'].feature_importances_
    feat_imp = pd.Series(importances, index=feature_names).sort_values(ascending=False)

    plt.figure(figsize=(10,6))
    sns.barplot(x=feat_imp[:15], y=feat_imp.index[:15], palette="magma", legend=False)
    plt.title(f"Top 15 Feature Importances - {structure_type} Regressor")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig(f"plots/{structure_type}_feature_importance.png", dpi=300)
    plt.close()

    dimension_models[structure_type] = reg_pipeline

joblib.dump(dimension_models, "models/dimension_regressors.pkl")

print("\n Training complete. Models saved in 'models/', plots saved in 'plots/'.")
