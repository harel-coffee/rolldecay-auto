"""
This module contains some covenient methods to get roll decay results from the DB
"""
import pandas as pd

import data
from sqlalchemy import create_engine
from mdldb.mdl_db import MDLDataBase

sql_template = """
SELECT * from
%s
INNER JOIN run
ON %s.run_id == run.id
    INNER JOIN loading_conditions
    ON (run.loading_condition_id == loading_conditions.id)
        INNER JOIN models
        ON run.model_number == models.model_number
            INNER JOIN ships
            ON models.ship_name == ships.name

"""

engine = create_engine('sqlite:///' + data.mdl_db_path)

def load(rolldecay_table_name='rolldecay_direct_improved',sql=None,only_latest_runs=True, limit_score=0.96):

    db = get_db()

    if sql is None:
        sql = sql_template % (rolldecay_table_name, rolldecay_table_name)

    df_rolldecay = pd.read_sql(sql, con=engine, index_col='run_id', )
    df_rolldecay = df_rolldecay.loc[:, ~df_rolldecay.columns.duplicated()]

    mask = df_rolldecay['score'] > limit_score
    df_rolldecay = df_rolldecay.loc[mask]

    if only_latest_runs:
        by = ['model_number', 'loading_condition_id', 'ship_speed']
        df_rolldecay = df_rolldecay.groupby(by=by).apply(func=get_latest)

    return df_rolldecay

def get_db():
    db = MDLDataBase(engine=engine)
    return db

def get_latest(group):
    """
    Get the latest run in this group:
    """
    s = group.sort_values(by=['date','run_number'], ascending=False).iloc[0]
    s['run_id'] = s.name
    return s
