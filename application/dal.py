from application.orm import BaseHelper


def get_settings(company_id):
    q = "SELECT video, liveness, frame FROM company_config where company_id = :_p"
    return BaseHelper.get_one(q, {"_p": company_id})


def get_credentials(company_id):
    q = "SELECT user, password FROM company WHERE company_id = :_p"
    return BaseHelper.get_one(q, {"_p": company_id})


def generate_token():
    q = "SELECT uuid() as token"
    return BaseHelper.get_one(q)


def set_token(tk, company_id):
    q = "UPDATE auth_token SET token = :_tk, update_date = now() WHERE company_id = :_p"
    return BaseHelper.query(q, {"_tk": tk,  "_p": company_id})


def get_token(company_id):
    q = "SELECT token FROM auth_token WHERE company_id = :_p"
    return BaseHelper.get_one(q, {"_p": company_id})

def save_log(kparams):
    q = BaseHelper.generate_insert_placeholder("log", kparams)
    return BaseHelper.query(q, kparams)