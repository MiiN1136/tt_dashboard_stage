# %%
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import joblib
import smtplib
from email.message import EmailMessage
import random
from datetime import datetime, timedelta, timezone
import pandas as pd
import hashlib
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import io
import os
import requests
from dotenv import load_dotenv

# %%
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

feature_names = joblib.load("features.pkl")
model = joblib.load("tt_healthcare_model1.1.pkl")

# Récupération des URLs secrètes depuis Render
url_risk = os.getenv("EMPLOYEE_RISK_DATA")
url_mycover = os.getenv("MYCOVER_DATA")
url_hr = os.getenv("FULL_HR_DATA")

# # Chargement distant sécurisé
df_employee_risk = pd.read_csv(url_risk) if url_risk else pd.DataFrame()
df_mycover = pd.read_csv(url_mycover) if url_mycover else pd.DataFrame()
full_hr = pd.read_csv(url_hr) if url_hr else pd.DataFrame()


# Local testing
# df_employee_risk = pd.read_csv("employee_risk1.1.csv")
# df_mycover = pd.read_csv("df_cleaned.csv")
# full_hr = pd.read_csv("full_hr.csv")


# MongoDB Atlas Connection
# load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["mycover_db"]
users_collection = db["users"]


class SignupRequest(BaseModel):
    matricule: str
    email: str
    password: str

class VerifyOtpRequest(BaseModel):
    matricule: str
    otp: str

class LoginRequest(BaseModel):
    role: str
    matricule: str = None
    password: str

class ForgotPasswordRequest(BaseModel):
    matricule: str
    email: str

class ResetPasswordRequest(BaseModel):
    matricule: str
    otp: str
    new_password: str

class ResendOTPRequest(BaseModel):
    matricule: str


def send_otp_email(receiver_email: str, otp_code: str):
    msg = EmailMessage()
    msg.set_content(f"Your TT Health Portal verification code is: {otp_code}\n\nThis code will expire in 10 minutes.")
    msg["Subject"] = "🔐 TT Health Portal - Account Activation Code"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@app.post("/api/login")
def login(data: LoginRequest):
    if data.role == "admin":
        if data.password == "admin123":
            return {"status": "success", "role": "admin"}
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
        
    elif data.role == "employee":
        query_matricule = int(data.matricule) if data.matricule.isdigit() else data.matricule
        
        user = users_collection.find_one({"matricule": str(data.matricule)})
        hashed_pw = hashlib.sha256(data.password.encode()).hexdigest()
        
        if not user or not user.get("password_hash"):
            # Check if matricule exists anywhere in the medical records dataset
            valid_employee = not df_mycover[df_mycover["Matricule"] == query_matricule].empty
            if valid_employee:
                return {"status": "first_time", "message": "Account not found or unassigned. Please sign up first."}
            raise HTTPException(status_code=404, detail="Matricule not found in medical registry.")
            
        if user["password_hash"] == hashed_pw:
            return {"status": "success", "role": "employee", "matricule": data.matricule}
        raise HTTPException(status_code=401, detail="Incorrect password.")


@app.post("/api/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    # Check if a verified user exists with this matricule and email
    user = users_collection.find_one({"matricule": str(data.matricule)})
    if not user or not user.get("is_verified", False):
        raise HTTPException(status_code=404, detail="No account found with this Matricule.")
    
    if user.get("email") != data.email:
        raise HTTPException(status_code=400, detail="The provided email does not match our records for this Matricule.")
    
    # Generate 6-digit OTP & 10-minute expiration
    otp_code = f"{random.randint(100000, 999999)}"
    otp_expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10)
    
    users_collection.update_one(
        {"matricule": str(data.matricule)},
        {
            "$set": {
                "otp_code": otp_code,
                "otp_expires_at": otp_expires_at
            }
        }
    )
    
    # Dispatch email
    send_otp_email(data.email, otp_code)
    return {"status": "otp_sent", "message": "Password reset code sent to your email."}

@app.post("/api/reset-password")
def reset_password(data: ResetPasswordRequest):
    user = users_collection.find_one({"matricule": str(data.matricule)})
    if not user:
        raise HTTPException(status_code=404, detail="User session not found.")
        
    # Check if OTP has expired
    expires_at = user.get("otp_expires_at")
    if expires_at:
        if expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)
        if datetime.now(timezone.utc).replace(tzinfo=None) > expires_at:
            raise HTTPException(status_code=400, detail="Reset code has expired. Please request a new one.")
            
    # Verify OTP
    if user.get("otp_code") != data.otp:
        raise HTTPException(status_code=400, detail="Invalid verification code.")
        
    hashed_pw = hashlib.sha256(data.new_password.encode()).hexdigest()
    
    # Update password and clear OTP tokens
    users_collection.update_one(
        {"matricule": str(data.matricule)},
        {
            "$set": {"password_hash": hashed_pw},
            "$unset": {"otp_code": "", "otp_expires_at": ""}
        }
    )
    return {"status": "success", "message": "Password successfully reset. Please log in."}


@app.post("/api/resend-otp")
def resend_otp(data: ResendOTPRequest):
    user = users_collection.find_one({"matricule": str(data.matricule)})
    if not user or not user.get("is_verified", False):
        raise HTTPException(status_code=404, detail="Active user account not found.")
    
    email = user.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="No corporate email found for this account.")
    
    # Generate new 6-digit OTP & 10-minute expiration
    otp_code = f"{random.randint(100000, 999999)}"
    otp_expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10)
    
    users_collection.update_one(
        {"matricule": str(data.matricule)},
        {
            "$set": {
                "otp_code": otp_code,
                "otp_expires_at": otp_expires_at
            }
        }
    )
    
    # Dispatch email
    send_otp_email(email, otp_code)
    return {"status": "otp_sent", "message": "A new verification code has been sent to your email."}

@app.post("/api/signup")
def signup(data: SignupRequest):
    query_matricule = int(data.matricule) if data.matricule.isdigit() else data.matricule
    
    # 1. Check registry
    valid_employee = not df_mycover[df_mycover["Matricule"] == query_matricule].empty
    if not valid_employee:
        raise HTTPException(status_code=404, detail="Matricule not found in medical registry.")
    
    # 2. Check if already verified by matricule
    existing_user = users_collection.find_one({"matricule": str(data.matricule)})
    if existing_user and existing_user.get("is_verified", False):
        raise HTTPException(status_code=400, detail="Account is already registered and verified.")
        
    # 2.5. Check if email already exists with an active/verified account
    existing_email = users_collection.find_one({"email": data.email, "is_verified": True})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already associated with an account.")
    
    # 3. Generate 6-digit OTP & set a 10-minute expiration window
    otp_code = f"{random.randint(100000, 999999)}"
    otp_expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10)
    hashed_pw = hashlib.sha256(data.password.encode()).hexdigest()
    
    # 4. Save pending account data with expiry timestamp
    users_collection.update_one(
        {"matricule": str(data.matricule)},
        {
            "$set": {
                "matricule": str(data.matricule),
                "email": data.email,
                "password_hash": hashed_pw,
                "otp_code": otp_code,
                "otp_expires_at": otp_expires_at,
                "is_verified": False
            }
        },
        upsert=True
    )
    
    # 5. Dispatch email
    send_otp_email(data.email, otp_code)
    
    return {"status": "otp_sent", "message": "Verification code sent to your email."}


@app.post("/api/verify-otp")
def verify_otp(data: VerifyOtpRequest):
    user = users_collection.find_one({"matricule": str(data.matricule)})
    
    if not user:
        raise HTTPException(status_code=404, detail="User session not found. Please sign up again.")
    
    if user.get("is_verified", False):
        raise HTTPException(status_code=400, detail="Account is already verified.")
    
    # Check if OTP has expired
    expires_at = user.get("otp_expires_at")
    if expires_at:
    # Strip tzinfo if MongoDB returned it as aware, ensuring safe comparison
        if expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)
            
        if datetime.now(timezone.utc).replace(tzinfo=None) > expires_at:
            raise HTTPException(status_code=400, detail="Verification code has expired. Please sign up again.")
        
    # Check if OTP matches
    if user.get("otp_code") != data.otp:
        raise HTTPException(status_code=400, detail="Invalid verification code. Please check and try again.")
    
    # Activate account & clean up OTP fields
    users_collection.update_one(
        {"matricule": str(data.matricule)},
        {
            "$set": {"is_verified": True},
            "$unset": {"otp_code": "", "otp_expires_at": ""}
        }
    )
    
    return {"status": "success", "message": "Account successfully verified and activated."}

@app.get("/api/employee/records/{matricule}")
def get_employee_records(matricule: str):
    # Normalize matricule type to match df_mycover (string vs integer)
    query_matricule = int(matricule) if matricule.isdigit() else matricule
    
    # Query the dataframe safely
    employee_data = df_mycover[df_mycover["Matricule"] == query_matricule]

    employee_data = employee_data.replace({np.nan: None})
    
    if employee_data.empty:
        raise HTTPException(status_code=404, detail="Record not found in medical registry.")
        
    # Return your records as a dictionary/json
    return employee_data.to_dict(orient="records")

# %%
FEATURES = [
    "Dependent_Age",
    "Couple_TT",
    "Chronic_Disease_asthme",
    "Chronic_Disease_cancer",
    "Chronic_Disease_cardiaque",
    "Chronic_Disease_diabete",
    "Chronic_Disease_hypertension",
    "Chronic_Disease_troubles musculosquelettiques",
    "Chronic_Disease_aucune",
    "Type_Prestation_Clinique",
    "Type_Prestation_Consultation",
    "Type_Prestation_Laboratoire",
    "Type_Prestation_Pharmacie",
    "Type_Prestation_Radio"
]

# %%

def risk_score(cost):
    try:
        val = float(cost)
        
        if val < 80:
            return 20
        elif val < 175:
            return 50
        elif val < 500:
            return 75
        else:
            return 95
    except (ValueError, TypeError):
        return 0
    

def risk_level(score):
    if score < 40:
        return "Low Risk"
    elif score < 70:
        return "Medium Risk"
    elif score < 95:
        return "High Risk"
    else:
        return "Critical"


@app.post("/predict")
def predict(data: dict):

    df = pd.DataFrame([data])

    expected_features = list(model.feature_names_in_)

    # ensure all features exist
    for col in expected_features:
        if col not in df.columns:
            df[col] = 0

    if "Couple_TT" in df.columns:
        df["Couple_TT"] = df["Couple_TT"].astype(int)

    # remove extra columns if any
    df = df[expected_features]

    pred = float(model.predict(df)[0])

    score = risk_score(pred)
    level = risk_level(score)

    return {
        "predicted_cost": pred,
        "risk_score": score,
        "risk_level": level
    }


@app.get("/high-risk")
def get_high_risk():

    df = df_employee_risk.copy()

    X = df[list(model.feature_names_in_)]

    preds = model.predict(X)

    df["Predicted_Cost"] = preds
    df["Risk_Score"] = df["Predicted_Cost"].apply(risk_score)
    df["Risk_Level"] = df["Risk_Score"].apply(risk_level)

    high_risk_df = df[(df["Risk_Level"] == "High Risk") | (df["Risk_Level"] == "Critical")]

    return high_risk_df[
        ["Matricule", "Predicted_Cost", "Risk_Score", "Risk_Level"]
    ].to_dict(orient="records")


@app.get("/risk-distribution")
def risk_distribution():

    df = df_employee_risk.copy()

    # safe feature selection
    X = df[list(model.feature_names_in_)]

    preds = model.predict(X)

    df["Predicted_Cost"] = preds
    df["Risk_Score"] = df["Predicted_Cost"].apply(risk_score)
    df["Risk_Level"] = df["Risk_Score"].apply(risk_level)

    # clean aggregation
    result = df["Risk_Level"].value_counts().reset_index()
    result.columns = ["Risk_Level", "Count"]

    return result.to_dict(orient="records")


@app.get("/cost-by-disease")
def cost_by_disease():

    df = df_employee_risk.copy()

    disease_cols = [
        "Chronic_Disease_asthme",
        "Chronic_Disease_cardiaque",
        "Chronic_Disease_cancer",
        "Chronic_Disease_diabete",
        "Chronic_Disease_troubles musculosquelettiques",
        "Chronic_Disease_hypertension",
        "Chronic_Disease_aucune"
    ]

    result = []

    for col in disease_cols:
        total_cost = df[df[col] == 1]["Total_Depense"].sum()

        result.append({
            "Disease": col.replace("Chronic_Disease_", ""),
            "Total_Cost": int(total_cost)
        })

    return result


@app.get("/risk-heatmap-age")
def risk_heatmap_age():

    df = df_employee_risk.copy()

    X = df[list(model.feature_names_in_)].copy()
    X = X.fillna(0)

    df["Predicted_Cost"] = model.predict(X)
    df["Risk_Score"] = df["Predicted_Cost"].apply(risk_score)
    df["Risk_Level"] = df["Risk_Score"].apply(risk_level)

    # IMPORTANT: treat as categorical label (not real age)
    age_map = {
        0: "0-8",
        1: "9-16",
        2: "17-24",
        3: "25-32",
        4: "33-40",
        5: "41-48",
        6: "49-55",
        7: "56-63",
        8: "64-71",
        9: "72-79",
        10: "80-87",
        11: "+88"
    }

    df["Age_Bin"] = df["Dependent_Age"].map(age_map)

    heatmap = (
        df.groupby(["Age_Bin", "Risk_Level"])
        .size()
        .reset_index(name="Count")
    )

    return heatmap.to_dict(orient="records")


@app.get("/kpis")
def get_kpis():

    df = df_employee_risk.copy()
    X = df[list(model.feature_names_in_)].fillna(0)

    preds = model.predict(X)

    df["Predicted_Cost"] = preds

    return {
        "total_predicted_cost": float(df["Total_Depense"].sum()),
        "avg_cost": float(df["Predicted_Cost"].mean()),
        "high_risk_count": int((df["Predicted_Cost"] >= 500).sum()),
        "total_employees": len(df)
    }


@app.get("/cost-drivers")
def cost_drivers():

    df = df_employee_risk.copy()

    X = df[list(model.feature_names_in_)].fillna(0)
    y = df["Total_Depense"]

    from sklearn.ensemble import RandomForestRegressor
    temp_model = RandomForestRegressor(n_estimators=200, random_state=42)
    temp_model.fit(X, y)

    importance = pd.DataFrame({
        "Feature": X.columns,
        "Importance": temp_model.feature_importances_
    }).sort_values("Importance", ascending=False)

    return importance.to_dict(orient="records")[:3]



def compute_age(birth_date):
    today = pd.Timestamp("2026-06-01")
    return int((today - pd.to_datetime(birth_date)).days / 365.25)

full_hr["Employee_Age"] = full_hr["Date de Naissance"].apply(compute_age)

hr_age = full_hr[["Matricule", "Employee_Age"]]

df_mycover = df_mycover.merge(
    hr_age,
    on="Matricule",
    how="left"
)


def build_visit_features(df):

    return {
        "visits_clinique": int((df["Type_Prestation"] == "Clinique").sum()),
        "visits_consultation": int((df["Type_Prestation"] == "Consultation").sum()),
        "visits_laboratoire": int((df["Type_Prestation"] == "Laboratoire").sum()),
        "visits_pharmacie": int((df["Type_Prestation"] == "Pharmacie").sum()),
        "visits_radio": int((df["Type_Prestation"] == "Radio").sum()),
    }



@app.get("/employee/{matricule}")
def employee_view(matricule: int):

    df = df_mycover[df_mycover["Matricule"] == matricule].copy()

    visit_features = build_visit_features(df)

    if df.empty:
        return {"error": "Employee not found"}

    # ---------------------------
    # 1. GET EMPLOYEE AGE
    # ---------------------------
    employee_age = df["Employee_Age"].dropna().iloc[0]

    # ---------------------------
    # 2. BUILD PROFILE = RAW BULLETINS
    # ---------------------------
    profile = df[[
        "Dependent_Age",
        "Chronic_Disease",
        "Type_Prestation",
        "Date_Sinistre",
        "Date_Remboursement",
        "Etat",
        "Total_Depense",
        "Total_Rembourse",
        "Relationship"
    ]].copy()

    # clean NaN
    profile = profile.fillna("None")

    # ---------------------------
    # 3. BUILD MODEL INPUT (AGGREGATED ONLY FOR PREDICTION)
    # ---------------------------
    model_df = df.copy()

    # aggregate correctly for model
    X = {
        "Dependent_Age": employee_age,        
        # Maladies
        "Chronic_Disease_asthme": int((model_df["Chronic_Disease"] == "asthme").any()),
        "Chronic_Disease_diabete": int((model_df["Chronic_Disease"] == "diabete").any()),
        "Chronic_Disease_hypertension": int((model_df["Chronic_Disease"] == "hypertension").any()),
        "Chronic_Disease_troubles musculosquelettiques": int((model_df["Chronic_Disease"] == "troubles musculosquelettiques").any()),
        "Chronic_Disease_cancer": int((model_df["Chronic_Disease"] == "cancer").any()),
        "Chronic_Disease_cardiaque": int((model_df["Chronic_Disease"] == "cardiaque").any()),
        "Chronic_Disease_aucune": int((model_df["Chronic_Disease"].isna()).all() or (model_df["Chronic_Disease"] == "None").all()),

        # Prestations
        "Type_Prestation_Clinique": int((model_df["Type_Prestation"] == "Clinique").any()),
        "Type_Prestation_Consultation": int((model_df["Type_Prestation"] == "Consultation").any()),
        "Type_Prestation_Laboratoire": int((model_df["Type_Prestation"] == "Laboratoire").any()),
        "Type_Prestation_Pharmacie": int((model_df["Type_Prestation"] == "Pharmacie").any()),
        "Type_Prestation_Radio": int((model_df["Type_Prestation"] == "Radio").any()),
    }

    expected_features = list(model.feature_names_in_)

    X_df = pd.DataFrame([X])

    # force missing columns = 0
    for col in expected_features:
        if col not in X_df.columns:
            X_df[col] = 0

    # reorder EXACTLY like training
    X_df = X_df[expected_features]

    pred = float(model.predict(X_df)[0])

    # ---------------------------
    # 4. RETURN CLEAN BI STRUCTURE
    # ---------------------------
    return {
        "matricule": int(matricule),
        "employee_age": int(employee_age),
        "predicted_cost": pred,
        "visit_features": visit_features,
        "profile": profile.to_dict(orient="records")
    }


@app.get("/cohorts")
def cohorts():

    df = df_employee_risk.copy()

    X = df[list(model.feature_names_in_)].fillna(0)
    df["Predicted_Cost"] = model.predict(X)

    df["Age_Group"] = df["Dependent_Age"].map({
        0:"0-8",1:"9-16",2:"17-24",3:"25-32",
        4:"33-40",5:"41-48",6:"49-55",7:"56-63",
        8:"64-71",9:"72-79",10:"80-87",11:"+88"
    })

    result = df.groupby("Age_Group")["Predicted_Cost"].mean().reset_index()

    return result.to_dict(orient="records")


@app.post("/what-if")
def what_if(data: dict):

    reduce_clinic = data.pop("reduce_clinic", False)

    # build dataframe
    df = pd.DataFrame([data])

    expected_features = list(model.feature_names_in_)

    # ensure all columns exist
    for col in expected_features:
        if col not in df.columns:
            df[col] = 0

    # reorder EXACTLY like training
    df = df[expected_features]

    base_pred = float(model.predict(df)[0])

    # scenario simulation
    df_scenario = df.copy()

    if reduce_clinic:
        if "Type_Prestation_Clinique" in df_scenario.columns:
            df_scenario["Type_Prestation_Clinique"] = 0

    new_pred = float(model.predict(df_scenario)[0])

    return {
        "base_cost": base_pred,
        "scenario_cost": new_pred,
        "savings": base_pred - new_pred
    }


@app.get("/risk-matrix")
def risk_matrix():
    df = df_employee_risk.copy()

    X = df[list(model.feature_names_in_)].fillna(0)
    df["Predicted_Cost"] = model.predict(X)

    # Bin the predicted cost into Risk Levels
    df["Risk_Level"] = pd.cut(
        df["Predicted_Cost"],
        bins=[0, 100, 500, 2000, 10000],
        labels=["Low Risk", "Medium Risk", "High Risk", "Critical Risk"]
    )

    # Consolidate one-hot encoded diseases into a single primary dimension
    def get_primary_disease(row):
        if row.get("Chronic_Disease_diabete", 0) == 1: return "Diabetes"
        if row.get("Chronic_Disease_hypertension", 0) == 1: return "Hypertension"
        if row.get("Chronic_Disease_asthme", 0) == 1: return "Asthma"
        if row.get("Chronic_Disease_troubles musculosquelettiques", 0) == 1: return "Musculoskeletal"
        if row.get("Chronic_Disease_cancer", 0) == 1: return "Cancer"
        if row.get("Chronic_Disease_cardiaque", 0) == 1: return "Cardiaque"
        return "None"

    df["Disease_Type"] = df.apply(get_primary_disease, axis=1)

    # Group by the new Disease dimension
    grouped = df.groupby(["Risk_Level", "Type_Prestation_Clinique", "Disease_Type"])
    
    matrix = grouped.size().reset_index(name="Count")
    cost_matrix = grouped["Predicted_Cost"].mean().reset_index(name="Avg_Cost")
    
    final_matrix = pd.merge(matrix, cost_matrix, on=["Risk_Level", "Type_Prestation_Clinique", "Disease_Type"])
    final_matrix = final_matrix[final_matrix["Count"] > 0]
    final_matrix["Avg_Cost"] = final_matrix["Avg_Cost"].round(2)

    return final_matrix.to_dict(orient="records")


@app.get("/cost-trend")
def cost_trend():
    df = df_mycover.copy()

    df["Date_Sinistre"] = pd.to_datetime(df["Date_Sinistre"])
    df["Month"] = df["Date_Sinistre"].dt.to_period("M").astype(str)

    result = df.groupby("Month")["Total_Depense"].sum().reset_index()

    return result.to_dict(orient="records")


@app.get("/risk-trend")
def risk_trend():
    df = df_mycover.copy()

    df["Date_Sinistre"] = pd.to_datetime(df["Date_Sinistre"])
    df["Month"] = df["Date_Sinistre"].dt.to_period("M").astype(str)

    # derive risk level
    def assign_risk(row):
        score = risk_score(row["Total_Depense"])
        return risk_level(score)

    df["Risk_Level"] = df.apply(assign_risk, axis=1)

    result = df.groupby(["Month", "Risk_Level"]).size().reset_index(name="Count")

    return result.to_dict(orient="records")


@app.get("/clinic-trend")
def clinic_trend():
    df = df_mycover.copy()

    df["Date_Sinistre"] = pd.to_datetime(df["Date_Sinistre"])
    df["Month"] = df["Date_Sinistre"].dt.to_period("M").astype(str)

    result = df.groupby(["Month", "Type_Prestation"]).size().reset_index(name="Count")

    return result.to_dict(orient="records")


@app.get("/avg-cost-trend")
def avg_cost_trend():
    df = df_mycover.copy()

    df["Date_Sinistre"] = pd.to_datetime(df["Date_Sinistre"])
    df["Month"] = df["Date_Sinistre"].dt.to_period("M").astype(str)

    result = df.groupby("Month")["Total_Depense"].mean().reset_index()

    return result.to_dict(orient="records")