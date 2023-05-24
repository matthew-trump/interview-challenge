from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from models import business_symptom_association
from models import Symptom
from models import Business
from models import Symptom
from settings import get_env

router = APIRouter()


@router.get('/status')
async def get_status():
    try:
        return {"Health OK"}

    except Exception as e:
        return {'Error: ' + str(e)}


DB_HOST = get_env("DB_HOST", "localhost")
DB_NAME = get_env("DB_NAME", "postgres")
DB_USER = get_env("DB_USER", "postgres")
DB_PASSWORD = get_env("DB_PWD", "password")

DB_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


# Create an engine and session
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

@router.get("/data/{symptom_code}")
async def get_association_data(
    symptom_code: str,
    business_id: int = Query(None, title="Business ID"),
    diagnostic: str = Query(None, title="Symptom Code")
):
   
        query = session.query(business_symptom_association).filter(business_symptom_association.c.symptom_code==symptom_code)
        if business_id:
            query = query.filter(business_symptom_association.c.business_id==business_id)
        if diagnostic:
            query = query.filter(business_symptom_association.c.diagnostic==diagnostic)

        result = query.all()
       
        association_data = []
        # Obviously do this with a proper join if I
        for association in result:
            bQuery = session.query(Business).filter(Business.id==association.business_id).first()
            sQuery = session.query(Symptom).filter(Symptom.code==association.symptom_code).first()

            association_data.append(
                {
                "business_id": bQuery.id,
                "business_name": bQuery.name,
                "symptom_code": sQuery.code,
                "symptom_name": sQuery.name,
                "symptom_diagnostic": association.diagnostic,
                }
            )
        return association_data
    


    
@router.post('/csv/')
async def upload_csv(file: UploadFile=File(...)):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file format. Only CSV files are allowed.")
    
    try:
        contents = await file.read()
        decoded = contents.decode("utf-8")
        lines = decoded.split("\n")
        records = [line.split(",") for line in lines]
        
        if records[0][0] == "Business ID":
            records = records[1:]
        
        association_data = []
        for record in records:
            if(len(record)>=5):
                association_data.append({
                    'business_id' : record[0],
                    'symptom_code' : record[2],
                    'diagnostic' : bool(record[4]),
                    'created_by': 'matt',
                    'updated_by' : 'matt'
                })

        print(association_data)
        with engine.begin() as conn:
             stmt = insert(business_symptom_association).values(association_data)
             conn.execute(stmt)

        return {"message": "CSV file uploaded and data inserted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")






