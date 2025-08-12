import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from scipy.stats import iqr

def impute_missing_values(df, columns, method='median'):
    """Handles missing values in specified columns."""
    df_imputed = df.copy()
    numeric_cols = df_imputed[columns].select_dtypes(include=np.number).columns.tolist()
    
    if not numeric_cols:
        return df_imputed, "No numeric columns selected for imputation."

    if method == 'Mean':
        imputer = SimpleImputer(strategy='mean')
    elif method == 'KNN':
        imputer = KNNImputer(n_neighbors=5)
    else: # Median is the default
        imputer = SimpleImputer(strategy='median')
        
    df_imputed[numeric_cols] = imputer.fit_transform(df_imputed[numeric_cols])
    log_message = f"Imputed missing values in columns {numeric_cols} using {method}."
    return df_imputed, log_message

def handle_outliers(df, columns, method='IQR'):
    """Handles outliers in specified columns using IQR method."""
    df_outliers_handled = df.copy()
    log_messages = []
    
    # Only process columns that exist in the dataframe
    valid_columns = [col for col in columns if col in df_outliers_handled.columns]
    
    for col in valid_columns:
        if pd.api.types.is_numeric_dtype(df_outliers_handled[col]):
            Q1 = df_outliers_handled[col].quantile(0.25)
            Q3 = df_outliers_handled[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df_outliers_handled[(df_outliers_handled[col] < lower_bound) | (df_outliers_handled[col] > upper_bound)]
            if not outliers.empty:
                log_messages.append(f"Found {len(outliers)} outlier(s) in '{col}' using {method}.")
                # Capping the outliers (Winsorization)
                df_outliers_handled[col] = np.where(df_outliers_handled[col] < lower_bound, lower_bound, df_outliers_handled[col])
                df_outliers_handled[col] = np.where(df_outliers_handled[col] > upper_bound, upper_bound, df_outliers_handled[col])
                log_messages.append(f"Capped outliers in '{col}' at lower:{lower_bound:.2f} and upper:{upper_bound:.2f}.")
            else:
                log_messages.append(f"No outliers detected in '{col}' using {method}.")

    if not log_messages:
        log_messages.append("No numeric columns selected for outlier handling.")

    return df_outliers_handled, "\n".join(log_messages)

def apply_rules(df):
    """Applies a simple validation rule."""
    df_validated = df.copy()
    # Rule: If Age < 18, Employment_Status should not be 'Employed'.
    if 'Age' in df_validated.columns and 'Employment_Status' in df_validated.columns:
        violations = df_validated[(df_validated['Age'] < 18) & (df_validated['Employment_Status'] == 'Employed')]
        if not violations.empty:
            log_message = f"Found {len(violations)} rule violation(s): Age < 18 and Employed. Correcting status to 'Unemployed'."
            df_validated.loc[violations.index, 'Employment_Status'] = 'Unemployed'
        else:
            log_message = "No rule violations found."
    else:
        log_message = "Could not apply age/employment rule: required columns not found."
        
    return df_validated, log_message

def calculate_estimates(df, weight_column):
    """Calculates weighted and unweighted summary statistics."""
    if weight_column not in df.columns:
        return pd.DataFrame(), f"Weight column '{weight_column}' not found in the dataframe."
        
    summary = {}
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    
    for col in numeric_cols:
        if col != weight_column:
            # Drop rows where the variable or weight is NaN for accurate calculation
            valid_data = df[[col, weight_column]].dropna()
            if not valid_data.empty:
                unweighted_mean = valid_data[col].mean()
                weighted_mean = np.average(valid_data[col], weights=valid_data[weight_column])
                summary[col] = {'Unweighted Mean': unweighted_mean, 'Weighted Mean': weighted_mean}
            
    if not summary:
        return pd.DataFrame(), "No valid numeric columns to generate estimates for."

    summary_df = pd.DataFrame(summary).T.reset_index().rename(columns={'index': 'Variable'})
    log_message = f"Calculated weighted and unweighted means using '{weight_column}'."
    return summary_df, log_message
