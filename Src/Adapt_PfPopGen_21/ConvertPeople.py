from TableUtils import VTTable
import sys
import hashlib


basedir = 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04'

# Build index of all available studies
tableStudies=VTTable.VTTable()
tableStudies.allColumnsText=True
tableStudies.LoadFile(basedir+"/PartnerStudies.txt")
studiesMap = tableStudies.BuildColDict('Study', False)



tablePeople=VTTable.VTTable()
tablePeople.allColumnsText=True
tablePeople.LoadFile(basedir+"/PS_people.txt")

tablePeople.ColumnRemoveQuotes("Affiliation1")
tablePeople.ColumnRemoveQuotes("Affliliation2")
tablePeople.ColumnRemoveQuotes("LeadPartnerFor")
tablePeople.ColumnRemoveQuotes("KeyAssociateFor")
tablePeople.DropCol('Affiliation1')
tablePeople.DropCol('Affliliation2')
tablePeople.DropCol('Affiliation URL')

#Create ID
tablePeople.MergeColsToString('id', '{0}','Name')
tablePeople.MapCol('id', lambda st: st.lower().replace(' ','-').replace('.',''))

tablePeople.ArrangeColumns(['id'])
tablePeople.PrintRows(0,9999)

#check uniqueness of id's
tablePeople.BuildColDict('id', False)



#Split roles into normalised table

tableRoles=VTTable.VTTable()
tableRoles.AddColumn(VTTable.VTColumn('contact_person','Text'))
tableRoles.AddColumn(VTTable.VTColumn('study','Text'))

for RowNr in tablePeople.GetRowNrRange():
    personid=tablePeople.GetValue(RowNr,tablePeople.GetColNr('id'))
    studyListStr = tablePeople.GetValue(RowNr,tablePeople.GetColNr('LeadPartnerFor'))
    if len(studyListStr)>0:
        studylist=studyListStr.split(',')
        for study in studylist:
            if study not in studiesMap:
                raise Exception("Invalid study "+study)
            tableRoles.AddRowEmpty()
            RowNr2=tableRoles.GetRowCount()-1
            tableRoles.SetValue(RowNr2,0,personid)
            tableRoles.SetValue(RowNr2,1,study)
tableRoles.AddIndexCol('id')
tableRoles.PrintRows(0,9999)
tableRoles.SaveFile(basedir+'/Output/study_contact_person.txt', True, '')
tableRoles.SaveSQLDump(basedir+'/Output/study_contact_person.sql','study_contact_person')


#Prepare & save people table
tablePeople.DropCol('LeadPartnerFor')
tablePeople.DropCol('KeyAssociateFor')
tablePeople.DropCol('Previous_ContactPersonFor')
tablePeople.RenameCol('id', 'contact_person')
tablePeople.RenameCol('Name', 'name')
tablePeople.RenameCol('Email', 'email')
tablePeople.AddColumn(VTTable.VTColumn('description','Text'))
tablePeople.AddColumn(VTTable.VTColumn('image','Text'))
tablePeople.FillColumn('description', '')
tablePeople.FillColumn('image', '')
tablePeople.ArrangeColumns(['contact_person', 'description', 'email', 'image', 'name'])
tablePeople.PrintRows(0,9)
tablePeople.SaveFile(basedir+'/Output/contact_person.txt', True, '')
tablePeople.SaveSQLDump(basedir+'/Output/contact_person.sql','contact_person')
