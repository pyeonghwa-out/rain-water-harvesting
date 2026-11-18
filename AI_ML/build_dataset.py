import pandas as pd
import os
df=pd.read_csv("./data/raw/Bengaluru_talukwise/Bengaluru_rural.csv")

df.columns = (
    df.columns.str.strip()      
             .str.lower()        
             .str.replace(r"[^\w\s]", "", regex=True)  #
             .str.replace(" ", "_")   
)

df = df.dropna(subset=["lat", "long", "pre_2016"])

df["pre_2016"] = pd.to_numeric(df["pre_2016"], errors="coerce")
df = df.dropna(subset=["pre_2016"])

output_dir = "./data/processed/"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "bengaluru_rural.csv")
df.to_csv(output_path, index=False)

print(f"✅ Cleaned dataset saved at: {output_path}")
print("Final shape:", df.shape)