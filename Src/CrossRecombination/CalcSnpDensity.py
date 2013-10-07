from TableUtils import VTTable
import sys
import os
import math

mysqlcommand = '/usr/local/mysql/bin/mysql'
#mysqlcommand = 'mysql'


mysqldumpcommand = mysqlcommand+'dump'

crosses = [ '3d7_hb3', '7g8_gb4', 'hb3_dd2' ]
methods = [ 'cortex', 'gatk' ]

temppath = '/Users/pvaut/Documents/Data/Crosses'

winsize=1000

chromosomeInfo = [
            { 'id': 'Pf3D7_01_v3', 'len': int(0.640851E6) },
            { 'id': 'Pf3D7_02_v3', 'len': int(0.947102E6) },
            { 'id': 'Pf3D7_03_v3', 'len': int(1.067971E6) },
            { 'id': 'Pf3D7_04_v3', 'len': int(1.200490E6) },
            { 'id': 'Pf3D7_05_v3', 'len': int(1.343557E6) },
            { 'id': 'Pf3D7_06_v3', 'len': int(1.418242E6) },
            { 'id': 'Pf3D7_07_v3', 'len': int(1.445207E6) },
            { 'id': 'Pf3D7_08_v3', 'len': int(1.472805E6) },
            { 'id': 'Pf3D7_09_v3', 'len': int(1.541735E6) },
            { 'id': 'Pf3D7_10_v3', 'len': int(1.687656E6) },
            { 'id': 'Pf3D7_11_v3', 'len': int(2.038340E6) },
            { 'id': 'Pf3D7_12_v3', 'len': int(2.271494E6) },
            { 'id': 'Pf3D7_13_v3', 'len': int(2.925236E6) },
            { 'id': 'Pf3D7_14_v3', 'len': int(3.291936E6) }
            ]

chromosomes = [info['id'] for info in chromosomeInfo]



for cross in crosses:
    for method in methods:
        outfile = temppath+'/tmp.txt'

        tablename = 'SNPDENS_F_'+cross+'_'+method

        tbrs=VTTable.VTTable()
        tbrs.AddColumn(VTTable.VTColumn('chrom','Text'))
        tbrs.AddColumn(VTTable.VTColumn('pos','Value'))
        tbrs.AddColumn(VTTable.VTColumn('CntRaw','Value'))
        tbrs.AddColumn(VTTable.VTColumn('CntFlt','Value'))

        for chromoInfo in chromosomeInfo:
            chromoId=chromoInfo['id']
            chromoLen=chromoInfo['len']

            ptcount = chromoLen/winsize+1

            filter = "(cross_name='{0}')".format(cross)
            filter += " AND (method='{0}')".format(method)
            filter += " AND (chrom='{0}')".format(chromoId)

            # Data set 1 : unfiltered
            cmd = '{0} --user=root --password=1234 --column-names=TRUE pfx -e "SELECT chrom,pos from variants_filtered where {2}" > {1}'.format(
                mysqlcommand,
                outfile,
                filter)
            print(cmd)
            os.system(cmd)

            tb1=VTTable.VTTable()
            tb1.allColumnsText=True
            tb1.LoadFile(outfile)
            tb1.ConvertColToValue('pos')
            tb1.PrintRows(0,9)

            cts1 = [0]*ptcount
            for rownr in tb1.GetRowNrRange():
                pos = tb1.GetValue(rownr,1)
                bin = int(math.floor(pos/winsize))
                cts1[bin] += 1

            # Data set 2 : unfiltered
            filter += " AND (filter='')"
            cmd = '{0} --user=root --password=1234 --column-names=TRUE pfx -e "SELECT chrom,pos from variants_filtered where {2}" > {1}'.format(
                mysqlcommand,
                outfile,
                filter)
            print(cmd)
            os.system(cmd)

            tb2=VTTable.VTTable()
            tb2.allColumnsText=True
            tb2.LoadFile(outfile)
            tb2.ConvertColToValue('pos')
            tb2.PrintRows(0,9)


            cts2 = [0]*ptcount
            for rownr in tb2.GetRowNrRange():
                pos = tb2.GetValue(rownr,1)
                bin = int(math.floor(pos/winsize))
                cts2[bin] += 1

            for i in range(ptcount):
                tbrs.AddRowEmpty()
                rownr = tbrs.GetRowCount()-1
                tbrs.SetValue(rownr, 0, chromoId)
                tbrs.SetValue(rownr, 1, (i+0.5)*winsize)
                tbrs.SetValue(rownr, 2, cts1[i])
                tbrs.SetValue(rownr, 3, cts2[i])


        tbrs.PrintRows(0,20)
        tbrs.SaveFile(temppath+'/tb.txt')
        tbrs.SaveSQLCreation(temppath+'/f1.sql',tablename)
        tbrs.SaveSQLDump(temppath+'/f2.sql',tablename)

        cmd = '{0} --user=root --password=1234  pfx -e "SOURCE {1}"'.format(
            mysqlcommand,
            temppath+'/f1.sql'
        )
        print(cmd)
        os.system(cmd)

        cmd = '{0} --user=root --password=1234  pfx -e "SOURCE {1}"'.format(
            mysqlcommand,
            temppath+'/f2.sql'
        )
        print(cmd)
        os.system(cmd)

        #sys.exit()