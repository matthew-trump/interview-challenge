from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from models import Symptom
from models import Business
from models import SymptomCode
from settings import get_env, DB_URL, USER

router = APIRouter()

@router.get('/status')
async def get_status():
    try:
        return {"Health OK"}
    except Exception as e:
        return {'Error: ' + str(e)}

# Create an engine and session
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

@router.get('/symptoms/')
async def get_association_data(
    business_id: int = Query(None, title="Business ID"),
    diagnostic: str = Query(None, title="Symptom Code")
):
        query = session.query(Symptom)
        if business_id and is_valid_business_id(business_id):
            query = query.filter(Symptom.business_id==business_id)
        if diagnostic:
            query = query.filter(Symptom.symptom_diagnostic==parse_bool_from_string(diagnostic))

        result = query.all()
       
        symptoms = []

        for symptom in result:
            #bQuery = session.query(Business).filter(Business.id==association.business_id).first()
            #sQuery = session.query(Symptom).filter(Symptom.code==association.symptom_code).first()

            symptoms.append(
                {
                "Business ID":          symptom.business_id,
                "Business Name":        symptom.business.name,
                "Symptom Code":         symptom.symptom_code,
                "Symptom Name":         symptom.symptom.name,
                "Symptom Diagnostic":   symptom.symptom_diagnostic,
                }
            )
        return symptoms
    
async def parse_records_from_file(file):
    contents = await file.read()
    decoded = contents.decode("utf-8")
    lines = decoded.split("\n")
    records = [line.split(",") for line in lines]
    return records

def parse_bool_from_string(s:str):
    return s.lower() in ['true','yes']

def remove_header(records):
     try:
        int(records[0][0])
     except ValueError:
        records = records[1:] 
     return records

def is_valid_record(record):
    return len(record) > 4

def symptom_code_exists(code: str):
     symptomcode = session.query(SymptomCode).filter(SymptomCode.code==code).first()
     return symptomcode is not None

def business_exists(id: int):
     business = session.query(Business).filter(Business.id==id).first()
     return business is not None

def is_valid_symptom_code(code: str):
     return len(code)==9 and code[0:5]=='SYMPT'

def is_valid_business_id(id: str):
    try:
        int(id)
        return True
    except:
        return False

def update_symptom_codes_to_be_added(existing,record):
     updated = {**existing }
     if record[2] not in updated:
       updated[record[2]] =   { 'code' : record[2],  'name' : record[3], 'created_by': USER, 'updated_by' : USER }
     return updated

def update_businesses_to_be_added(existing,record):
     updated = {**existing }
     if record[0] not in updated:
       updated[record[0]] =   { 'id' : int(record[0]),  'name' : record[1], 'created_by': USER, 'updated_by' : USER }
     return updated
    
@router.post('/business_symptoms/')
async def upload_business_symptoms_csv(file: UploadFile=File(...)):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file format. Only CSV files are allowed.")
    
    try:
        records = await parse_records_from_file(file)
        records = remove_header(records)
    
        symptoms_to_be_added = []
        symptom_codes_to_be_added = {}
        businesses_to_be_added = {}

        for record in records:
            if is_valid_record(record):
                valid_system_code = False
                valid_business_id = False
                if is_valid_symptom_code(record[2]):
                     valid_system_code = True
                     if not symptom_code_exists(record[2]):
                        symptom_codes_to_be_added = update_symptom_codes_to_be_added(symptom_codes_to_be_added,record)
                if is_valid_business_id(record[0]):
                     valid_business_id = True
                     if not business_exists(int(record[0])):
                        businesses_to_be_added = update_businesses_to_be_added(businesses_to_be_added,record)
                
                if valid_system_code and valid_business_id:
                      symptoms_to_be_added.append({
                          'business_id' : int(record[0]),
                          'symptom_code' : record[2],
                          'symptom_diagnostic' : parse_bool_from_string(record[4]),
                          'created_by': USER, 
                          'updated_by' : USER,   
                      })
                                                                             
        list_of_system_codes_to_be_added = list(symptom_codes_to_be_added.values())
        list_of_businesses_to_be_added   = list(businesses_to_be_added.values())

        with engine.begin() as conn:
              if len(list_of_system_codes_to_be_added) > 0:
                stmt = insert(SymptomCode).values(list_of_system_codes_to_be_added)
                conn.execute(stmt)
              if len(list_of_businesses_to_be_added) > 0:
                stmt = insert(Business).values(list_of_businesses_to_be_added)
                conn.execute(stmt)
              if len(symptoms_to_be_added) > 0:
                stmt = insert(Symptom).values(symptoms_to_be_added)
                conn.execute(stmt)

        message = {"message": "CSV file uploaded and data inserted successfully."}
        if len(list_of_system_codes_to_be_added) > 0:
            message['system_codes'] = list_of_system_codes_to_be_added
        if len(list_of_businesses_to_be_added ) > 0:
            message['businesses'] = list_of_businesses_to_be_added
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")






