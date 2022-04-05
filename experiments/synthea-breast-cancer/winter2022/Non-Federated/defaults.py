'''defaults.py: A file with default constant variables to ensure safety of get commands for dictionaries'''

DEFAULT_MEDS = []
DEFAULT_PROCEDURES = []
DEFAULT_LABEL = {'label': None}
DEFAULT_GROUP = {'dataValue': DEFAULT_LABEL}
DEFAULT_SUBJECT = {"date_of_birth": None, "sex": None}
DEFAULT_STAGING = [{'stageGroup': DEFAULT_GROUP, 'primaryTumorCategory': DEFAULT_GROUP, 'regionalNodesCategory': DEFAULT_GROUP}]
DEFAULT_CANCER_CONDITION = [{'tnmStaging': DEFAULT_STAGING, "dateOfDiagnosis": None, 'code': DEFAULT_LABEL}]
DEFAULT_QUERY = '''
query{
  katsuDataModels
  {
    mcodeDataModels
    {
      mcodePackets{
        subject {
          dateOfBirth
          sex
        }
        cancerCondition {
          dateOfDiagnosis
          tnmStaging{
            stageGroup {
              dataValue {
                label
              }
            }
            primaryTumorCategory{
              dataValue{
                label
              }
            }
            regionalNodesCategory{
              dataValue{
                label
              }
            }
          }
          code{
            label
          }
        }
        cancerRelatedProcedures {
          procedureType
        }
        cancerDiseaseStatus {
          label
        }
        medicationStatement {
          medicationCode {
            label
          }
        }
      }
    }
  }
}
'''