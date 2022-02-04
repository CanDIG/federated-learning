'''parsers.py: A module with helper functions/classes to support the EDA parsing process in SyntheaEDA.ipynb'''

import re
from defaults import *
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class Patient:
    cancer_status: Optional[int] = None
    age: Optional[float] = None
    sex: Optional[int] = None
    stage: Optional[int] = None
    primary: Optional[int] = None
    nodes: Optional[int] = None
    meds: Optional[Dict[str, Any]] = None
    procedures: Optional[Dict[str, Any]] = None
    cancer_type: Optional[str] = None


class UniqueInfoParser:
    def __init__(self, patient_info_json) -> None:
        self.patient_info_json = patient_info_json
    
    '''get_uniq_procedures(): returns a List of strings containing the unique procedure types within the collected data'''
    def get_uniq_procedures(self) -> List[str]:
        procedures = []
        for patient in self.patient_info_json:
            procs = [procedure.get('procedureType') for procedure in patient.get('cancerRelatedProcedures', DEFAULT_PROCEDURES)]
            procedures.extend(procs)
            
        return list(set(procedures))
    
    '''get_uniq_meds(): returns a List of strings containing the unique medication types within the collected data'''
    def get_uniq_meds(self) -> List[str]:
        meds = []
        for patient in self.patient_info_json:
            patient_meds = [med.get('medicationCode').get('label') for med in patient.get('medicationStatement', DEFAULT_MEDS)]
            meds.extend(patient_meds)
            
        return list(set(meds))


class PatientInfoParser:
    def __init__(self, uniq_meds: List[str], uniq_procedures: List[str], patient: Optional[Dict[str, Any]]) -> None:
        self.uniq_meds = uniq_meds
        self.uniq_procedures = uniq_procedures
        self.patient = patient

        self.type = self.__get_cancer_type()
        self.meds = self.__get_patient_meds()
        self.age = self.__encode_one_hot_age() / 365.25
        self.sex = self.__encode_one_hot_sex()
        self.stages = self.__encode_one_hot_stage()
        self.status = self.__encode_one_hot_status()
        self.procedures = self.__get_patient_procedures()
        self.stage = self.stages['stage']
        self.nodes = self.stages['nodes']
        self.primary = self.stages['primary']

    
    '''get_patient_data(): Passed in an Optional JSON Object in the form of a Dictionary, and returns a Patient Object
            with the specified cancer information'''
    def get_patient_data(self) -> Patient:
        return Patient(self.status, self.age, self.sex, self.stage, self.primary, self.nodes, self.meds, self.procedures, self.type)

    ''' __encode_one_hot_sex(): Returns an Optional integer with 1 for a female sex specified and 0 otherwise'''
    def __encode_one_hot_sex(self) -> Optional[int]: 
        sex = self.patient.get('subject', DEFAULT_SUBJECT).get('sex')

        if sex is not None: 
            if sex == 'FEMALE': return 1
            return 0
        
        return None

    '''__encode_one_hot_age(): Returns an optional integer specifying the number of days between the date of diagnosis
            and the date of birth of the patient'''
    def __encode_one_hot_age(self)-> Optional[int]:
        age = self.patient.get('subject', DEFAULT_SUBJECT).get('dateOfBirth')
        diag = self.patient.get('cancerCondition', DEFAULT_CANCER_CONDITION)[0].get('dateOfDiagnosis')

        if age is not None and diag is not None: return self.__get_age(age, diag)
        return None

    '''__encode_one_hot_status(): Returns an optional integer where 1 represents an improvement in patient health and 0 represents a   
            decline in patient health'''
    def __encode_one_hot_status(self) -> Optional[int]:
        cancer_status = self.patient.get('cancerDiseaseStatus', DEFAULT_LABEL)

        if cancer_status is not None: return self.__get_status(cancer_status.get('label'))
        return None
    
    '''__ encode_one_hot_stage(): Returns a Dictionary with values representing the stage of the cancer/tumour/nodes'''
    def __encode_one_hot_stage(self) -> Dict[str, int]:
        stage, primary, nodes = None, None, None
        cancer_stagings = self.patient.get('cancerCondition', DEFAULT_CANCER_CONDITION)[0].get('tnmStaging')

        if cancer_stagings is not None:
            stage_group = cancer_stagings[0].get('stageGroup', DEFAULT_GROUP)
            stage = self.__get_stage(stage_group.get('dataValue', DEFAULT_LABEL).get('label', None))

            primary_group = cancer_stagings[0].get('primaryTumorCategory', DEFAULT_GROUP)
            primary = self.__get_primary(primary_group.get('dataValue', DEFAULT_LABEL).get('label', None))

            nodes_group = cancer_stagings[0].get('regionalNodesCategory', DEFAULT_GROUP)
            nodes = self.__get_nodes(nodes_group.get('dataValue', DEFAULT_LABEL).get('label', None))

        return {'stage': stage, 'primary': primary, 'nodes': nodes}
    
    '''__get_cancer_type(): Passed in a JSON Object in the form of a dictionary and returns an optional string corresponding to 
            the cancer type'''
    def __get_cancer_type(self) -> Optional[str]:
        return self.patient.get('cancerCondition', DEFAULT_CANCER_CONDITION)[0].get('code', DEFAULT_LABEL).get('label', None)
    
    '''__get_patient_meds(): Returns a Dictionary with string keys and int values that display the unique medications as keys and 
            display the number of times the specified patient takes the given medication as its value'''
    def __get_patient_meds(self) -> Dict[str, int]:
        meds = self.patient.get('medicationStatement', DEFAULT_MEDS)

        meds_dict = dict.fromkeys(self.uniq_meds, 0)
        for med in meds:
            meds_dict[med.get('medicationCode').get('label')] += 1
        
        return meds_dict

    '''__get_patient_procedures(): Returns a Dictionary of string keys and int values where the keys represent the different procedure 
            types and the values represent the number of times that procedure was performed on the specified patient'''
    def __get_patient_procedures(self) -> Dict[str, int]:
        procedures = self.patient.get('cancerRelatedProcedures', DEFAULT_PROCEDURES)

        procedures_dict = dict.fromkeys(self.uniq_procedures, 0)
        for procedure in procedures:
            procedures_dict[procedure.get('procedureType')] += 1
        
        return procedures_dict

    ''' __get_age(age, diag): Passed in two strings, age and diag corresponding do the date of birth and date of diagnosis of the
            patient, respectively, and returns an integer specifying the number of days between the two events'''
    def __get_age(self, age: str, diag: str) -> int:
        date_of_birth = datetime.strptime(age, "%Y-%m-%d")
        date_of_diagnosis = datetime.strptime(diag, "%Y-%m-%dT%H:%M:%SZ")
        diff = date_of_diagnosis - date_of_birth
        return diff.days

    '''__get_status(cancer_status): Passed in a string, this function returns an integer value representing either an improvement or
            decline in the patient's health'''
    def __get_status(self, cancer_status: str) -> int:
        if cancer_status == "Patient's condition improved": return 1
        return 0

    '''__get_stage(given_stage): Passed in a str, this function returns the patient's cancer stage'''
    def __get_stage(self, given_stage: str) -> Optional[int]:
        if re.search(r'[sS]tage 1', given_stage): return 1
        if re.search(r'[sS]tage 2', given_stage): return 2
        if re.search(r'[sS]tage 3', given_stage): return 3
        if re.search(r'[sS]tage 4', given_stage): return 4
        return None

    '''__get_primary(given_stage): Passed in a str, this function returns the patient's tumour stage'''
    def __get_primary(self, given_stage: str) -> Optional[int]:
        if 'T0' in given_stage: return 0
        if 'T1' in given_stage: return 1
        if 'T2' in given_stage: return 2
        if 'T3' in given_stage: return 3
        if 'T4' in given_stage: return 4
        return None

    '''__get_nodes(given_stage): Passed in a str, this function returns the patient's nodes stage'''
    def __get_nodes(self, given_stage: str) -> Optional[int]:
        if 'N0' in given_stage: return 0
        if 'N1' in given_stage: return 1
        if 'N2' in given_stage: return 2
        if 'N3' in given_stage: return 3
        return None
