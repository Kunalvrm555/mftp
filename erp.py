from os import environ as env
from bs4 import BeautifulSoup as bs
import sys
import re
import get_otp
import time
from main import session

ERP_HOMEPAGE_URL = 'https://erp.iitkgp.ac.in/IIT_ERP3/welcome.jsp'
ERP_LOGIN_URL = 'https://erp.iitkgp.ac.in/SSOAdministration/auth.htm'
ERP_SECRET_QUESTION_URL = 'https://erp.iitkgp.ac.in/SSOAdministration/getSecurityQues.htm'
ERP_OTP_URL = 'https://erp.iitkgp.ac.in/SSOAdministration/getEmilOTP.htm' # blame ERP for the typo
ERP_CDC_MODULE_URL = 'https://erp.iitkgp.ac.in/IIT_ERP3/menulist.htm?module_id=26'
ERP_TPSTUDENT_URL = 'https://erp.iitkgp.ac.in/TrainingPlacementSSO/TPStudent.jsp'

req_args = {
    'timeout': 20,
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/46.0.2490.86 Safari/537.36',
        'Referer':
        'https://erp.iitkgp.ac.in/SSOAdministration/login.htm?sessionToken=595794DC220159D1CBD10DB69832EF7E.worker3',
    },
    'verify': False
}


class WrongPasswordError(Exception):
    pass


class SecretAnswerError(Exception):
    pass


def erp_login(session):
    print ("Started ERP_Login!")

    r = session.get(ERP_HOMEPAGE_URL, **req_args)
    soup = bs(r.text, 'html.parser')

    print ("Length of the fetched HTML: " + str(len(str(r.text))))
    
    if (r.status_code == 404):
        print("Previous Session is still alive.")
        return
    
    if soup.find(id='sessionToken'):
        sessionToken = soup.find(id='sessionToken').attrs['value']
    else:
        raise Exception("Could not get the sessionToken!")

    r = session.post(ERP_SECRET_QUESTION_URL, data={'user_id': env['ERP_USERNAME']},
               **req_args)
    secret_question = r.text

    if secret_question is None:
        raise WrongPasswordError("Failed to fetch secret question: please check that username and password are valid!")

    print ("Secret question from the ERP: " + secret_question)
    secret_answer = None
    secret_answer_index = None
    for i in range(1, 4):
        # print (env['ERP_Q%d' % i])
        if env['ERP_Q%d' % i] == secret_question:
            secret_answer = env['ERP_A%d' % i]
            secret_answer_index = i
            break

    if secret_answer is None:
        print ('No secret question matched:', secret_question)
        sys.exit(1)

    # Handling OTP
    r = session.post(ERP_OTP_URL, data={'typeee': 'SI', 'loginid': env['ERP_USERNAME']}, **req_args) #because 'type' was too mainstream for ERP
    time.sleep(15)
    otp = get_otp.get_otp()


    login_details = {
        'user_id': env['ERP_USERNAME'],
        'password': env['ERP_PASSWORD'],
        'answer': secret_answer,
        'email_otp': otp,
        'sessionToken': sessionToken,
        'requestedUrl': 'https://erp.iitkgp.ac.in/IIT_ERP3/welcome.jsp',
    }

    r = session.post(ERP_LOGIN_URL, data=login_details,
               **req_args)

    if len(r.history) < 2:
        print("{answer} (ERP_A{index}) is wrong for {question}".format(
            answer=secret_answer,
            index=secret_answer_index,
            question=secret_question
        ))
        raise SecretAnswerError("Please check your secret answer settings!")

    ssoToken = re.search(r'\?ssoToken=(.+)$',
                         r.history[1].headers['Location']).group(1)

    print ("ERP Login completed!")
    r = session.get("https://erp.iitkgp.ac.in/IIT_ERP3/?%s" % ssoToken, **req_args)

    print ("Started TNP Login!")
    
    session.post(ERP_TPSTUDENT_URL,  # headers=headers,
                 data=dict(ssoToken=ssoToken, menu_id=11, module_id=26),
                 **req_args)
    print ("TNP Login completed!")
    
    # Saving session tokens in a file, so that others can access it
    with open('.session_token', 'w') as f:
        f.write(f"ssoToken = {ssoToken}\nsessionToken = {sessionToken}")
