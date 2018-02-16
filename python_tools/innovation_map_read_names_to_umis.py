__author__ = 'pererad1'

import csv, sys


csv.field_size_limit(sys.maxsize)

# Input file:
#
# HWI-D00444:335:H5K2YADXX:1:2116:6346:85692    1   74169   74268
#
# HWI-D00444:335:H5K2YADXX:1:2116:6346:85692	129	1	74169	0	100M	=	2297499	2223331	ATGAACTCATCATTTTTTATGGCTGCATAGTATTCCATGGTGTATATGTGCCACATTTTCTTAATCCAGTCTATCATTGTTGGACATTTGGGTTGGTTCC	???<>D=A=??>>@@??@==A?ACEC>=;D=<>?DC@=DF;?/7<:6C=ACE@E>@AA?ADA<@?AC?F=DA:@D>=AF>?EF?@>???GFE=?EC>==<	BD:Z:KKNNOOONONONNKCCCCKJMNNNOONNKNNNKKLMNNNOMKKNKKKNKKOONKKNKCCLLKKKLOMNONOLMKONNKLKMLOMNLOLDMPKOONQMMLM	PG:Z:MarkDuplicates.2	RG:Z:BG742590-N	BI:Z:NNPPPOQLPONONLEEEENOOOOQRPRONQQONMNNPOPPQOOOOOOPOOQPPONOMFFNNMONOONPRQONPOOPOMPOOPPPPNONGQQNRPQQQONN	NM:i:0	BQ:Z:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@	MQ:i:0	OQ:Z:?>?;=B=@=?@==??>>?==@>@ABA=<;B<<>=A@@<AA:?08::5A<@AA@A=???>@B?<>@@@>D=A@;?A>=?C@@BD=@>?AADCA<>B@<<><	AS:i:100	XS:i:100
# HWI-D00444:335:H5K2YADXX:1:2204:9038:67796	65	1	74209	0	100M	=	40836025	40761817	TGTATATGTGCCACATTTTCTTAATCCAGTCTATCATTGTTGGACATTTGGGTTGGTTCCAAGTCTTTGCTATTGTGAATAATGCCGCAATAAACATACG	?A=:><=E>FBD<D???@@?D@>>?GE>F==?;?D?>?D=>ED;:==>?DBB<?AE<><C=@@<A@<<AA?5=<=<?9;<6><>??:?9;;5;;=9;9<<	BD:Z:KKKNMMLOLKOONKJMJBBKKJJJKNLNONOLMKONNKLKMLOMMKNKCLOJMMLOMMLMNLMNOLKCLOOMKKLKKNMLKKLNOOMNOMMLMEOMNKMM	PG:Z:MarkDuplicates.2	RG:Z:BG742590-N	BI:Z:NNOOOOOPONPOONMNLEEMMLNMNNMORQNMONNOOMPOOPPOPNOMFPPMQOPPQONNPOOQONMFPQQPOMPOOPOOONOPQPQRSPPPOGQPOOOP	NM:i:0	BQ:Z:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@	MQ:i:0	OQ:Z:?A<9=;;B=CAB<A??>??>B?>=?CA=C=<?;?A@>>B==BB<:===>B@@;=@A;=<@=>@;??<<@?>3=<=;?:;;8=;===9=:9:7::<::8=<	AS:i:100	XS:i:100

# Becomes -->
#
# @K00217:116:HM7N7BBXX:5:2205:28554:10000:TCG+GAG
# TCG-GAG
# +
# -,86,,;
# @K00217:116:HM7N7BBXX:5:1208:22780:36464:ACC+TAT
# ACC-TAT
# +
# -,86,,;

input_file = str(sys.argv[1])
output_file = open(str(sys.argv[2]), 'w')

with open(input_file, 'rU') as csv_file:
    csv_reader1 = csv.reader(csv_file, delimiter='\t')

    for row in csv_reader1:
        row_split = str(row[0]).split(":")
        UMI = row_split[len(row_split) - 1]

        umi_split = UMI.split("+")
        duplexUMI = umi_split[0] + "-" + umi_split[1]
        content = '@' + str(row[0]) + "\n" + str(duplexUMI) + "\n+\n-,86,,;\n"
        output_file.write(content)

output_file.close()
