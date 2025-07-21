import requests

import csv
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    Date, DateTime, Boolean, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


PAYLOAD = {"general":{"network":"active","adm":[],"networkOrgCode":[],"satelliteName":[],"serviceType":"all"},"satNetworkTypes":{"geo":True,"geoFrom":None,"geoTo":None,"nonGeo":True,"apogeeFrom":None,"apogeeTo":None,"perigeeFrom":None,"perigeeTo":None,"minAltitudeFrom":None,"minAltitudeTo":None,"referenceBody":None,"constelattion":False,"shortDurationMission":False},"frequencies":[],"regProcess":{"SuppressionStatus":"All","masterReg":False,"nonPlanBand":False,"bssPlanBand":False,"fssPlanBand":False,"nonPlan":{"advancePublications":True,"coordination":True,"dueDiligence":True,"notification":True,"planNon":True,"res35":True},"bssPlan":{"downRegion1and3":True,"feederRegion1and3":True,"overallRegion2":True,"planBssAll":True,"pendingArt4":True,"listArt4":True,"dueDiligence":True,"notificationArt5":True,"sofArt2aCoordination":True,"sofArt2aNotification":True,"planBss":True},"fssPlan":{"planFssAll":True,"planFss":True,"pendingArt6":True,"listArt6":True,"dueDiligence":True,"notificationArt8":True}},"publications":{"latestBrIfic":False,"brIficNumberFrom":None,"brIficNumberTo":None,"brIficDateFrom":None,"brIficDateTo":None,"specialSection":[],"specialSectionNumber":None},"regDates":{"brNoticeDateReceiptFrom":None,"brNoticeDateReceiptTo":None,"networkProtectionDateFrom":None,"networkProtectionDateTo":None,"useDateFrom":None,"useDateTo":None,"useLimitDateFrom":None,"useLimitDateTo":None},"orderBy":""}
HEADERS = {
    "Content-Type": "application/json"
}
DB_URL = "sqlite:///itu_space.db"

Base = declarative_base()


class ImportSession(Base):
    __tablename__ = 'import_sessions'
    id = Column(Integer, primary_key=True)
    imported_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    # relation vers les enregistrements de fréquences
    assignments = relationship("FrequencyAssignment", back_populates="session")


class FrequencyAssignment(Base):
    __tablename__ = 'frequency_assignments'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('import_sessions.id'), nullable=False)
    ntc_id = Column(String, nullable=False)
    adm = Column(String)
    ntwk_org = Column(String)
    sat_name = Column(String)
    long_nom = Column(String)         # longitude nominale
    ntc_type = Column(String)
    ntf_rsn = Column(String)
    prov = Column(String)
    f_plan = Column(Boolean)
    plan_type = Column(String)
    plan_txt = Column(String)
    d_rcv = Column(Date)
    emi_rcp = Column(String)
    freq_from = Column(Float)
    freq_to = Column(Float)

    session = relationship("ImportSession", back_populates="assignments")

# ---------- Setup Database ----------
engine = create_engine(DB_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# ---------- Download & Insert Data ----------

def download_csv():
    response = requests.post("https://www.itu.int/itu-r/space/apps/ep/spaceexplorer/v1/queries/exportIncludingFrequencies/csv", 
                             json=PAYLOAD, 
                             headers=HEADERS)
    response.raise_for_status()
    return response.text


def import_data(csv_text: str):
    session = Session()
    imp = ImportSession()
    session.add(imp)
    session.flush()  # pour générer imp.id

    reader = csv.DictReader(csv_text.splitlines())
    for row in reader:
        # conversion des types
        d_rcv = datetime.strptime(row['d_rcv'], '%d.%m.%Y').date() if row['d_rcv'] else None
        freq_from = float(row['freq_from']) if row['freq_from'] else None
        freq_to = float(row['freq_to']) if row['freq_to'] else None
        f_plan = row['f_plan'].lower() == 'true'

        fa = FrequencyAssignment(
            session_id=imp.id,
            ntc_id=row['ntc_id'],
            adm=row['adm'],
            ntwk_org=row.get('ntwk_org'),
            sat_name=row['sat_name'],
            long_nom=row.get('long_nom'),
            ntc_type=row['ntc_type'],
            ntf_rsn=row['ntf_rsn'],
            prov=row['prov'],
            f_plan=f_plan,
            plan_type=row.get('plan_type'),
            plan_txt=row.get('plan_txt'),
            d_rcv=d_rcv,
            emi_rcp=row.get('emi_rcp'),
            freq_from=freq_from,
            freq_to=freq_to
        )
        session.add(fa)

    session.commit()
    session.close()
    print(f"Import terminé: session # {imp.id}")


if __name__ == '__main__':
    csv_data = download_csv()
    import_data(csv_data)