import VTTable
import sys


def PrintColumnStates(tb, colname):
    statelist = tb.GetColStateCountList(colname)
    print('\n================= states for {0} ==================='.format(colname))
    for id in statelist:
        print(str(statelist[id]) + '\t' + str(id))
    print('====================================================\n')

def PrintCorrespondence(tb, colname1, colname2):
    statelist = tb.GetColStateCountList(colname1)
    colnr1 = tb.GetColNr(colname1)
    colnr2 = tb.GetColNr(colname2)
    print('\n================= correspondence for {0} - > {1} ==================='.format(colname1, colname2))
    for state in statelist:
        othervals = {}
        for rownr in tb.GetRowNrRange():
            vl1 = tb.GetValue(rownr,colnr1)
            if vl1 == state:
                vl2 = tb.GetValue(rownr,colnr2)
                if vl2 not in othervals:
                    othervals[vl2] = 0;
                othervals[vl2] += 1
        cnt = len([k for k in othervals])
        print(str(cnt) + ' | ' + str(state) + ' | ' + str(othervals))
    print('====================================================\n')



if True:
    Dt31 = VTTable.VTTable()
    Dt31.allColumnsText = True
    Dt31.LoadFile("/Users/pvaut/Documents/Genome/PfPopgen31/samplesReport31.txt")

    # Remove excluded samples
    tmp = VTTable.VTTable()
    tmp.FilterValueFrom(Dt31, 'Exclude', "FALSE")
    Dt31 = tmp
    # Remove uneccesary columns
    Dt31.DropCol('Num')
    Dt31.DropCol('Version')
    Dt31.DropCol('LabSample')
    Dt31.DropCol('LowTypability')
    Dt31.DropCol('PcaOutlier')
    Dt31.DropCol('IsDuplicate')
    Dt31.DropCol('ManualExlusion')
    Dt31.DropCol('StudyCode')
    Dt31.DropCol('Exclude')
    # Rename columns to make specific
    Dt31.RenameCol('Study','Dt31_Study')
    Dt31.RenameCol('Country','Dt31_Country')

    #Dt31.PrintRows(0,10)
    #sys.exit()

if True:
    DtWebApp21 = VTTable.VTTable()
    #DtWebApp21.sepchar = ','
    DtWebApp21.allColumnsText = True
    DtWebApp21.LoadXls("/Users/pvaut/Documents/Genome/PfPopgen31/metadata-2.2_withsites.xlsx", "metadata-2.2_withsites.txt")

    # Remove excluded samples
    tmp = VTTable.VTTable()
    tmp.FilterValueFrom(DtWebApp21, 'Exclude', 0)
    DtWebApp21 = tmp
    # Remove uneccesary columns
    DtWebApp21.DropCol('LabSample')
    DtWebApp21.DropCol('LowTypability')
    DtWebApp21.DropCol('PcaOutlier')
    DtWebApp21.DropCol('IsDuplicate')
    DtWebApp21.DropCol('ManualExlusion')
    DtWebApp21.DropCol('UsedInSnpDiscovery')
    DtWebApp21.DropCol('Num')
    DtWebApp21.DropCol('Year')
    DtWebApp21.DropCol('Country')
    DtWebApp21.DropCol('KhCluster')
    DtWebApp21.DropCol('SubCont')
    DtWebApp21.DropCol('Site')
    DtWebApp21.DropCol('SiteInfoSource')
    DtWebApp21.DropCol('Notes')
    DtWebApp21.DropCol('SiteCodeOriginal')
    DtWebApp21.DropCol('Fws')
    DtWebApp21.DropCol('Typability')
    DtWebApp21.DropCol('Exclude')
    # Rename columns to make specific
    DtWebApp21.RenameCol('Study','WebApp_Study')
    DtWebApp21.RenameCol('Location','WebApp_Location')
    DtWebApp21.RenameCol('Region','WebApp_Region')
    DtWebApp21.RenameCol('SiteCode','WebApp_SiteCode')



if True:
    DtSolaris = VTTable.VTTable()
    DtSolaris.LoadXls("/Users/pvaut/Documents/Genome/PfPopgen31/solaris sample locations BM.xlsx", "PF_locations_extended.csv")
    #DtSolaris.PrintRows(0,10)
    #statelist = DtSolaris.GetColStateCountList('region')
    # for id in statelist:
    #     print(str(statelist[id]) + '\t' + id)
    DtSolaris.DropCol('Sample ID')
    # Rename columns
    DtSolaris.RenameCol('Oxford Code', 'Sample')
    DtSolaris.RenameCol('Project Code', 'Sol_study')
    DtSolaris.RenameCol('biosample_location', 'Sol_location')
    DtSolaris.RenameCol('region', 'Sol_region')
    DtSolaris.RenameCol('latitude', 'Sol_latitude')
    DtSolaris.RenameCol('longitude', 'Sol_longitude')
    DtSolaris.RemoveEmptyRows()

#sys.exit()

#PrintColumnStates(DtWebApp21, 'WebApp_SiteCode')

tmp = VTTable.VTTable()
tmp.MergeTablesByKeyFrom(Dt31, DtWebApp21, 'Sample', False, False)
#tmp.PrintRows(0, 1000000)
#PrintColumnStates(tmp, 'WebApp_SiteCode')

data = VTTable.VTTable()
data.MergeTablesByKeyFrom(tmp, DtSolaris, 'Sample', True, False)
#data.PrintRows(0, 10)

#PrintColumnStates(data, 'WebApp_SiteCode')

if True:
    print('************************* Info for samples present in webapp *******************************')
    tmp = data.FilterByFunctionReturn(lambda vl: (vl is not None) and (len(str(vl))>0), 'WebApp_SiteCode')
    PrintCorrespondence(tmp,'Sol_region', 'WebApp_SiteCode')
    PrintCorrespondence(tmp,'WebApp_SiteCode', 'Sol_region')


    #tmp2 = data.FilterByFunctionReturn(lambda a, b: (a=='KH_Pursat') and (b=='Ratanakiri'), 'WebApp_SiteCode', 'Sol_region')
    tmp2 = tmp.FilterByFunctionReturn(lambda a: (a=='PFV2'), 'Sol_study')
    tmp2.PrintRows(0,9999)
    tmp2.SaveFile('/Users/pvaut/Documents/Genome/PfPopgen31/tmp.txt')




set21 = data.FilterByFunctionReturn(lambda vl: (vl is not None) and (len(str(vl))>0), 'WebApp_SiteCode')
set31diff = data.FilterByFunctionReturn(lambda vl: (vl is None) or (len(str(vl))==0), 'WebApp_SiteCode')


if False:
    print('DETERMINING REGION STATES THAT ARE NEW TO 3.1')
    set21_sol_region_states = set21.GetColStateCountList('Sol_region')
    print(str(set21_sol_region_states))

    set31diff_sol_region_states = set31diff.GetColStateCountList('Sol_region')
    print(str(set31diff_sol_region_states))

    print(' *** 21 set size: {0}'.format(set21.GetRowCount()))
    print(' *** 31 diff set size: {0}'.format(set31diff.GetRowCount()))
    print('==== NEW STATES 31 diff ====')
    for state in set31diff_sol_region_states:
        if state not in set21_sol_region_states:
            tmp01 = data.FilterByFunctionReturn(lambda vl: vl == state, 'Sol_region')
            # country = tmp01.GetValue(0,tmp01.GetColNr('Sol_location'))
            # study = tmp01.GetValue(0,tmp01.GetColNr('Sol_study'))
            st = state
            countries = tmp01.GetColStateCountList('Sol_location')
            for country in countries:
                st += '\t' + country
            studies = tmp01.GetColStateCountList('Sol_study')
            for study in studies:
                st += '\t' + study + ':' + str(studies[study])
            print(st)
            # print('{0}\t{1}\t{2}\t{3}'.format(state, country, study, set31diff_sol_region_states[state]))
            # print('    {0}'.format(str(tmp01.GetColStateCountList('Sol_location'))))
            # print('    {0}'.format(str(tmp01.GetColStateCountList('Sol_study'))))

    print('==== STATES 31 diff also present in 21 ====')
    for state in set31diff_sol_region_states:
        if state in set21_sol_region_states:
            print('{0} : {1}'.format(state, set31diff_sol_region_states[state]))


if False:
    print('DETERMINING STUDIES THAT ARE NEW TO 3.1')
    set21_sol_studies = set21.GetColStateCountList('Sol_study')
    print(str(set21_sol_studies))

    set31diff_sol_studies = set31diff.GetColStateCountList('Sol_study')
    print(str(set31diff_sol_studies))

    print(' *** 21 set size: {0}'.format(set21.GetRowCount()))
    print(' *** 31 diff set size: {0}'.format(set31diff.GetRowCount()))
    print('==== NEW STUDIES 31 diff ====')
    for state in set31diff_sol_studies:
        if state not in set21_sol_studies:
            tmp01 = data.FilterByFunctionReturn(lambda vl: vl == state, 'Sol_study')
            st = state
            countries = tmp01.GetColStateCountList('Sol_location')
            for country in countries:
                st += '\t' + country
            studies = tmp01.GetColStateCountList('Sol_study')
            for study in studies:
                st += '\t' + study + ':' + str(studies[study])
            print(st)
            # print('{0}\t{1}\t{2}\t{3}'.format(state, country, study, set31diff_sol_region_states[state]))
            # print('    {0}'.format(str(tmp01.GetColStateCountList('Sol_location'))))
            # print('    {0}'.format(str(tmp01.GetColStateCountList('Sol_study'))))

    print('==== STUDIES 31 diff also present in 21 ====')
    for study in set31diff_sol_studies:
        if study in set21_sol_studies:
            tmp01 = data.FilterByFunctionReturn(lambda vl: vl == study, 'Sol_study')
            webappstudies = tmp01.GetColStateCountList('WebApp_Study')
            print('{0} : {1} | {2}'.format(study, set31diff_sol_studies[study], str(webappstudies)))


if False:
    print('DISCREPANCIES IN STUDY ID BETWEEN WEBAPP & SOLARIS')
    tmp01 = data.FilterByFunctionReturn(lambda study_web, study_sol: (study_web is not None) and (len(study_web)>0) and (study_web!=study_sol), 'WebApp_Study', 'Sol_study')
    tmp01.PrintRows(0,99999)

if True:
    print('DISCREPANCIES IN Country BETWEEN 3.1 Olivo & SOLARIS')
    tmp01 = data.FilterByFunctionReturn(lambda study_31, study_sol: (study_31!=study_sol), 'Dt31_Study', 'Sol_study')
    tmp01.PrintRows(0,99999)
