import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


BINARY_COLS = [
    "Partner", "Dependents", "PhoneService", "PaperlessBilling",
    "MultipleLines", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies",
]

CATEGORICAL_COLS = ["InternetService", "Contract", "PaymentMethod"]

NUMERIC_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]

TARGET_COL = "Churn"


def load_and_clean(raw_path: str) -> pd.DataFrame:
    df = pd.read_csv(raw_path)

    df = df.drop(columns=["customerID"])

    # TotalCharges arrives as string with some empty values
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df = df.dropna(subset=["TotalCharges"])

    return df


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    le = LabelEncoder()

    # Yes/No columns → 1/0
    for col in BINARY_COLS:
        df[col] = df[col].map({"Yes": 1, "No": 0, "No phone service": 0, "No internet service": 0})

    # Multi-class categoricals → one-hot
    df = pd.get_dummies(df, columns=CATEGORICAL_COLS, drop_first=True)

    # Gender
    df["gender"] = le.fit_transform(df["gender"])

    # Target
    df[TARGET_COL] = (df[TARGET_COL] == "Yes").astype(int)

    # Cast all int columns to float64 so MLflow schema allows NaN at inference time
    int_cols = df.select_dtypes(include="integer").columns
    df[int_cols] = df[int_cols].astype("float64")

    return df


def split(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)


def load_data(raw_path: str, test_size: float = 0.2, random_state: int = 42):
    df = load_and_clean(raw_path)
    df = encode_features(df)
    return split(df, test_size=test_size, random_state=random_state)
