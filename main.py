from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import json
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

app = FastAPI()
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive.readonly']
ZENDESK_URL = 'https://hevodata.zendesk.com/api/v2/tickets.json'

#credentials of the service acoount that reads from the Google sheet. 
CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
templates = Jinja2Templates(directory="templates")

# logging is set up but not completly implemented, using print statements for logging. 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Customer emails sheet details
user_inputs = {
    "DOCUMENT_NAME": None,
    "worksheet_number": None,
    "email_col_index": None}

@retry(
    stop=stop_after_attempt(5),  # Retry up to 5 times
    wait=wait_exponential(multiplier=1, min=4, max=10),  # Exponential backoff
    retry=retry_if_exception_type(requests.exceptions.ConnectionError)  # Retry on connection errors
    )

def fetch_user_id(email, auth):
    #takes in the email of the requestor and will return their internal zendesk user_id.
    #this is required as the api only supports adding public comment author by their user_id
    search_url = f'https://hevodata.zendesk.com/api/v2/users/search.json?query=email:{email}'
    headers = {'Content-Type': 'application/json'}
    response = requests.get(search_url, headers=headers, auth=auth)
    user_data = response.json()
    return user_data['users'][0]['id']

def replace_placeholders(body, placeholders, row):
    text = '__placeholder__'
    for i in range(len(placeholders)):
        key = text + str(i+1)
        value = list(placeholders.keys())[i]
        body = body.replace(key, value)

    text = '__placeholder_value__'
    for i in range(len(placeholders)):
        key = text + str(i+1)
        value = row[list(placeholders.values())[i]]
        body = body.replace(key, value)
    
    return body

def create_ticket(assignee_email, subject, req_email, tags, body, password, user_id):

    #adding emails in cc
    email_ccs = []
    email_array = assignee_email.split(',')
    if len(email_array) > 1:
        for email in email_array:
            d = {}
            d["action"] = "put"
            d["user_email"] = email
            email_ccs.append(d)

    #comment data
    comment = {}
    comment['author_id'] = user_id
    comment['body'] = str(body)

    data = {
        "ticket": {
            "subject": subject,
            "email_ccs": email_ccs,
            "requester": {'email': email_array[0]},
            "comment": comment,
            "assignee_email": req_email,
            "tags": tags
        }
    }

    headers = {"Content-Type": "application/json"}
    
    #return {"status": "success", "message": "Ticket created successfully. Ticket ID: 12345"}
    try:
        logger.info(f"Creating ticket with data:")
        print('--------------------------')
        print('url: ',ZENDESK_URL)
        print('headers: ', headers)
        print("auth: ", req_email, password)
        print(data)
        print('--------------------------')
        response = requests.post(ZENDESK_URL, headers=headers, json=data, auth=(req_email, password),timeout=15) 
        # request read timeout is set as 15 seconds, if we do not get a response back in 15 seconds, the request will be terminated and response will be assumed as 400.
        
        print('the response for the above is:',response.json())
        return {"status": "success", "message": f"Ticket created successfully. Ticket ID: {response.json()}"}
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create ticket: {e}")
        return {"status": "error", "message": f"Failed to create ticket: {e}"}

def read_gsheet_and_get_col_values(DOCUMENT_NAME, credentials, worksheet_number, email_col_index):
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open(DOCUMENT_NAME)
    worksheet = spreadsheet.get_worksheet(worksheet_number)
    values = worksheet.get_all_values()
    assignee_list = []

    for row in values:
        assignee_list.append(row[email_col_index])

    return [assignee_list,values]

@app.post("/set-params/", response_class=HTMLResponse)
async def set_params(
    request: Request,
    document_name: str = Form(...),
    worksheet_number: int = Form(...),
    email_col_index: int = Form(...)):
    
    global user_inputs
    global rows
    user_inputs["DOCUMENT_NAME"] = document_name
    user_inputs["worksheet_number"] = worksheet_number
    user_inputs["email_col_index"] = email_col_index
    
    values = read_gsheet_and_get_col_values(user_inputs["DOCUMENT_NAME"], CREDENTIALS, user_inputs["worksheet_number"], user_inputs["email_col_index"])
    assignee_list = values[0]
    rows = values[1]
    return templates.TemplateResponse("index.html", {"request": request, "assignee_list": assignee_list})

@app.post("/create-ticket/", response_class=HTMLResponse)
async def create_ticket_endpoint(
    request: Request,
    req_email: str = Form(...),
    password: str = Form(...),
    subject: str = Form(...),
    tags: str = Form(...),
    body: str = Form(...),
    placeholders: str = Form(...)):

    global user_inputs
    global rows
    placeholders_dict = json.loads(placeholders)
    responses = []
    user_id = fetch_user_id(req_email, auth=(req_email,password))
    iteration = 0
    
    for row in rows:
        #The ticket createion loop runs for 50 iterations, and then waits for 20 seconds to not go overboard with zendesk API rate limits. 
        if iteration==0:
            pass

        elif iteration%50 == 0:
            time.sleep(20)
        
        replaced_body = replace_placeholders(body,placeholders_dict,row) #replaced the placeholders in the body.txt
        response = create_ticket(assignee_email=row[user_inputs["email_col_index"]], subject=subject, req_email=req_email, tags=tags.split(','), body=replaced_body, password=password, user_id = user_id)
        responses.append({"email": row[user_inputs["email_col_index"]], "response": response})
        iteration = iteration+1

    return templates.TemplateResponse("index.html", {"request": request, "results": responses})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})