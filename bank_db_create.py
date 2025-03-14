import numpy as np
import pandas as pd
from faker import Faker
import sqlite3

# Initialise faker to generate random data
fake = Faker()

# Setting random seed for reproducibility
np.random.seed(42)

# Generating dataframe for a customer table
num_customers = 1200

customers_df = pd.DataFrame({
    'customer_id': np.arange(1, num_customers + 1),   # Nomial data (unique identifier for customer)
    'name':  [fake.name() for _ in range(num_customers)], # Nominal data (Customer Name)
    'age':  np.random.randint(18, 80, num_customers),  # Ratio data (Age in year)
    'gender' : np.random.choice(['Male', 'Female','Other'], num_customers),  # Nominal data (Gender)
    'credit_score':  np.random.randint(300, 850, num_customers),  # Ordinal data (300-850 scale) 
    'account_open_year' : np.random.randint(2021, 2025, num_customers),  # Interval data (Opening year 2021 to 2025)
    'income' : np.round(np.random.lognormal(np.log(30000), 1, num_customers), 2)  # Ratio data (Income)
})


# Inserted null values in age & income 
customers_df.loc[np.random.choice(customers_df.index, size=int(num_customers * 0.05),  replace=False), 'age'] = np.nan
customers_df.loc[np.random.choice(customers_df.index, size=int(num_customers * 0.03),  replace=False), 'income'] = np.nan

# print(customers_df.isnull().sum())

# Inserted duplicat value 
customers_df = pd.concat([customers_df, customers_df.sample(18)])

# print(customers_df.duplicated().sum())

# Generating dataframe for branch table
num_branch = 100

branches_df = pd.DataFrame({
    'branch_id': np.arange(1, num_branch + 1),
    'branch_name': [fake.company() for _ in range(num_branch)],
    'branch_location': [fake.city() for _ in range(num_branch)],
    'manager_name': [fake.name() for _ in range(num_branch)],
})

# Generate dataframe for Account Table
num_accounts = 1400
accounts_df = pd.DataFrame({
    "account_id": np.arange(1, num_accounts + 1),  # Unique account ID
    "customer_id": np.random.choice(customers_df["customer_id"], num_accounts),  # ForeignKey to Customers
    "branch_id": np.random.choice(branches_df["branch_id"], num_accounts),
    "balance": np.round(np.random.lognormal(np.log(5000), 1, num_accounts), 2),  # Ratio Data
    "account_type": np.random.choice(["Checking", "Savings", "Current"], num_accounts), # Nominal Data (Account Type)
})

# Generate dataframe for Transactions Table with Compound Key (account_id + transaction_date)
num_transactions = 2000
transactions_df = pd.DataFrame({
    "transaction_id": np.arange(1, num_transactions + 1),
    "account_id": np.random.choice(accounts_df["account_id"], num_transactions),  # ForeignKey to Accounts
    "transaction_date": pd.to_datetime(
    np.random.choice(pd.date_range('2021-01-01', '2025-12-31'), num_transactions)
) + pd.to_timedelta(np.random.randint(0, 86400, num_transactions), unit='s'),
    "transaction_type": np.random.choice(["Deposit", "Withdrawal", "Transfered"], num_transactions),
    "transaction_amount": np.round(np.random.lognormal(4.6, 1.0, num_transactions), 2),
    "transaction_status": np.random.choice(['Completed', 'Pending', 'Failed'], num_transactions, p=[0.6, 0.2, 0.2])  # Nominal data
})

# Generating dataframe for a Loans table
num_loans = 500

# Filter customers with credit score > 700
high_credit_customers = customers_df[customers_df['credit_score'] > 700]

# Create dataframe
loans_df = pd.DataFrame({
    'loan_id': np.arange(1, num_loans + 1),
    'customer_id': np.random.choice(high_credit_customers["customer_id"], num_loans),  # Foreign Key,
    'loan_amount': np.round(np.random.uniform(10000, 50000, num_loans),2),  # Ratio data,
    'interest_rate': np.random.uniform(5.0, 15.0, num_loans),  # Ratio data,
    'loan_status': np.random.choice(['Approved', 'Pending', 'Rejected'], num_loans),  # Nominal data,
    'duration_months': np.random.randint(6, 180, num_loans)  # Interval data
})


# print(customers_df.isnull().sum())

# Save data to CSV files
customers_df.to_csv('customer.csv', index=False)
accounts_df.to_csv('account.csv', index=False)
transactions_df.to_csv('transaction.csv', index=False)
branches_df.to_csv('branch.csv', index=False)
loans_df.to_csv('loan.csv', index=False)

conn = sqlite3.connect('Banking_db.db')

# Adding constraints to the tables
conn.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER CHECK(age >= 18 AND age <= 80),
    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
    credit_score INTEGER CHECK(credit_score BETWEEN 300 AND 850),
    account_open_year INTEGER CHECK(account_open_year >= 2021 AND account_open_year <= 2025),
    income REAL CHECK(income >= 0)
);
''')


conn.execute('''
CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    balance REAL CHECK(balance >= 0),
    account_type TEXT CHECK(account_type IN ('Savings', 'Checking', 'Current')),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS branches (
    branch_id INTEGER PRIMARY KEY,
    branch_name TEXT NOT NULL,
    branch_location TEXT NOT NULL,
    manager_name TEXT NOT NULL
);
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL,
    transaction_date DATE,
    transaction_type TEXT CHECK(transaction_type IN ('Deposit', 'Withdrawal', 'Transfer', 'Payment')),
    transaction_amount REAL CHECK(transaction_amount > 0),
    transaction_status TEXT CHECK(transaction_status IN ('Completed', 'Pending', 'Failed')),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS loans (
    loan_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    loan_amount REAL CHECK(loan_amount > 0),
    interest_rate REAL CHECK(interest_rate >= 5.0 AND interest_rate <= 15.0),
    loan_status TEXT CHECK(loan_status IN ('Approved', 'Pending', 'Rejected')),
    duration_months INTEGER CHECK(duration_months >= 6 AND duration_months <= 180),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
''')

# DataFrames to SQLite database tables
customers_df.to_sql('customers', conn, index=False, if_exists='replace')
accounts_df.to_sql('accounts', conn, index=False, if_exists='replace')
transactions_df.to_sql('transactions', conn, index=False, if_exists='replace')
branches_df.to_sql('branches', conn, index=False, if_exists='replace')
loans_df.to_sql('loans', conn, index=False, if_exists='replace')

# Close connection
conn.commit()
conn.close()