# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 14:40:08 2025

@author: elisa
"""

from commonfunc.db_handler import DbHandler
from dataprocess.tech_indicator import TechnicalIndicators

# get data
db = DbHandler()

crypto = 'BTC'
table_name = f"{crypto.lower()}_hourly"
query = f'select * from {table_name}'
df = db.read_from_db(query)

# compute technical metrics
ti = TechnicalIndicators(df.copy())
df_all = ti.compute_all_indicators()  # returns new df with many indicators

df_all = df_all[df_all['utc_dt']>='2020-01-01']

# define target variable
df_all['higher_1d'] = (df_all['close'].shift(-24) > df_all['close']).astype(int)
df_all['change_4h'] = (df_all['close'].shift(-4) - df_all['close'])/df_all['close']
df_all['higher_4h'] = (df_all['close'].shift(-4) > df_all['close']).astype(int)
df_all['higher_2h'] = (df_all['close'].shift(-2) > df_all['close']).astype(int)

threshold = 0.004

df_all['y_4h'] = 0  # Default to 0 (neutral)
df_all.loc[df_all['change_4h'] > threshold, 'y_4h'] = 1  # Upward movement
df_all.loc[df_all['change_4h'] < -threshold, 'y_4h'] = -1  # Downward movement

# handling missing data
df_all = df_all.dropna()
df_all.reset_index(inplace=True, drop=True)

# process features
# some need to be scaled based on its current value
var_to_scale = ['sma_24','sma_72','ema_24','ema_72',
                'bollinger_upper_24','bollinger_lower_24','atr_14',
                'macd','macd_signal']

for v in var_to_scale:
    df_all[f"{v}_scaled"] = df_all[v]/df_all['close']
    
# compute diff between macd and its signal
df_all['macd_diff'] = df_all['macd_scaled'] - df_all['macd_signal_scaled']

# compute sacled diff between open and close
df_all['close_diff'] = (df_all['close'] - df_all['open'] )/df_all['open']

# select features
features = ['sma_24_scaled','sma_72_scaled','ema_24_scaled','ema_72_scaled',
                'bollinger_upper_24_scaled','bollinger_lower_24_scaled',
                'atr_14_scaled',
                'macd_scaled','macd_signal_scaled',
                'macd_diff','close_diff',
                'rsi_14', 'macd', 'macd_signal', 'stoch_osc_14', 'stoch_rsi_14',
                'cci_20', 'adx_14', 'plus_di_14', 'minus_di_14',
                'volumefrom']

# classification model
X = df_all[features]
y = df_all['y_4h']

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Train-test split
split_idx = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

# Train model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Predict
y_pred = clf.predict(X_test)

# Evaluate
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2%}")
print(classification_report(y_test, y_pred))


# try logistic regression
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X = df_all[features]
y = df_all['y_4h']

# Normalize Data (for logistic regression & SVM)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Time-Series Split (Train on past, test on recent)
split_idx = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

X_train_scaled, X_test_scaled = X_scaled[:split_idx], X_scaled[split_idx:]

lr = LogisticRegression()
lr.fit(X_train_scaled, y_train)

y_pred = lr.predict(X_test_scaled)

print(f"Accuracy: {accuracy_score(y_test, y_pred):.2%}")
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred,labels = [-1,0,1]))


corr = X.corr()






